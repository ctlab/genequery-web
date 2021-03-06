import logging
import os
import json
from time import time
import urllib
import urllib2
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.html import format_html
from django.views.generic import View

from genequery.searcher.idconvertion import ToEntrezConversion, ToSymbolConversion, ToEntrezOrthologyConversion
from genequery.utils.constants import ENSEMBL
from math.fisher_empirical import FisherCalculationResult, calculate_fisher_p_values
from genequery.main.views import BaseTemplateView
from genequery.searcher.forms import SearchQueryForm
from genequery.searcher.models import ModuleDescription, GQModule
from genequery.utils import log_get, gene_list_pprint, here

LOG = logging.getLogger('genequery')

HTML_NEG_INF = format_html('-&infin;')


class JsonErrorResponse(JsonResponse):
    def __init__(self, error_message, status_code=500, **kwargs):
        super(JsonErrorResponse, self).__init__({
            'error': error_message,
            'code': status_code,
        }, **kwargs)


def get_module_heat_map_url(species, gse, gpl, module_number):
    """
    :type module_number: int
    :type gpl: str
    :type gse: str
    :type species: str
    :rtype: str
    """
    path_to_image = here('heatmaps', species, '{}_{}_module_{}.svg'.format(gse, gpl, module_number))
    if getattr(settings, 'MEDIA_ARE_LOCAL', False):
        path = here(settings.MEDIA_ROOT, path_to_image)
        return here(settings.MEDIA_URL, path_to_image) if os.path.exists(path) else None
    return here(settings.MEDIA_URL, path_to_image)


def get_gmt_url(species, gse, gpl):
    """
    :type species: str
    :type gpl: str
    :type gse: str
    """
    path_to_file = here('gmt', '{}_{}.gmt'.format(gse, gpl))
    if getattr(settings, 'MEDIA_ARE_LOCAL', False):
        path = here(settings.MEDIA_ROOT, path_to_file)
        return here(settings.MEDIA_URL, path_to_file) if os.path.exists(path) else None
    return here(settings.MEDIA_URL, path_to_file)


class SearchPageView(BaseTemplateView):
    template_name = 'search.html'
    menu_active = 'searcher'

    def get_context_data(self, **kwargs):
        context = super(SearchPageView, self).get_context_data()
        context['request_url'] = reverse('searcher:search')  # for ajax search request
        return context

    def get(self, request, **kwargs):
        request.META["CSRF_COOKIE_USED"] = True
        return render(request, self.template_name, self.get_context_data())

search_page_view = SearchPageView.as_view()


class SearchProcessorView(View):
    @log_get(LOG)
    def post(self, request):
        if not request.is_ajax():
            LOG.warning('Search request must be AJAX.')
            return JsonErrorResponse('Method not allowed', status_code=405)

        form = SearchQueryForm(request.POST)
        if not form.is_valid():
            LOG.info('Invalid form data: {}'.format('\n'.join(form.get_error_messages_as_list())))
            return JsonResponse({'error': ('\n'.join(form.get_error_messages_as_list()))})

        original_notation = form.get_genes_id_type()
        query_species = form.cleaned_data['query_species']
        db_species = form.cleaned_data['db_species']

        original_to_clean_genes = form.get_original_to_clean_genes_dict()
        LOG.info('GET request: genes {}, query_species {}, db_species: {}, query type: {}.'.format(
            gene_list_pprint(original_to_clean_genes.keys()), query_species, db_species, original_notation))

        start_time = time()

        genes = list(set(original_to_clean_genes.values()))
        if query_species == db_species:
            id_convertion = ToEntrezConversion.convert(db_species, original_notation, genes)
        else:
            id_convertion = ToEntrezOrthologyConversion.convert(query_species, db_species, original_notation, genes)
        input_entrez_ids = id_convertion.get_final_entrez_ids()

        if not input_entrez_ids:
            return JsonResponse(build_search_result_data(
                [],
                0,
                db_species,
                original_notation,
                id_convertion,
                original_to_clean_genes,
            ))

        try:
            sorted_results = calculate_fisher_process_results(db_species, input_entrez_ids)
        except:
            LOG.exception('Error while calculating p-values')
            return JsonErrorResponse('System error')

        processing_time = round(time() - start_time, 3)

        return JsonResponse(build_search_result_data(
            sorted_results,
            processing_time,
            db_species,
            original_notation,
            id_convertion,
            original_to_clean_genes,
        ))


search_processor_view = SearchProcessorView.as_view()


def _replace_dict_keys(dictionary, key_map, original_notation):
    """
    :type dictionary: dict[int, list] | dict[str, list]
    :type key_map: dict[str, str]
    :type original_notation: str
    :rtype dict[str, int] | dict[str, str]
    """
    if dictionary is None:
        return None

    res = {}
    for original_key, key in key_map.items():
        res[original_key] = dictionary[key]
    return res


def id_conversion_to_response(original_notation, id_conversion, original_to_clean_genes):
    """
    :type original_notation: str
    :type id_conversion: ToEntrezConversion | ToEntrezOrthologyConversion
    :type original_to_clean_genes: dict[str, str]
    :rtype: dict
    """
    result = {
        'orthology': False,
        'showProxyColumn': False,
        'to_entrez_conversion': {},
        'to_proxy_entrez_conversion': None,
        'original_notation': original_notation,
        'unique_entrez_count': len(id_conversion.get_final_entrez_ids()),
    }
    if isinstance(id_conversion, ToEntrezOrthologyConversion):
        result['orthology'] = True
        result['showProxyColumn'] = original_notation == ENSEMBL
        result['to_entrez_conversion'] = _replace_dict_keys(id_conversion.to_final_entrez,
                                                            original_to_clean_genes,
                                                            original_notation)
        result['to_proxy_entrez_conversion'] = _replace_dict_keys(id_conversion.to_proxy_entrez,
                                                                  original_to_clean_genes,
                                                                  original_notation)
    else:
        result['to_entrez_conversion'] = _replace_dict_keys(id_conversion.to_entrez,
                                                            original_to_clean_genes,
                                                            original_notation)

    return result


def build_search_result_data(
        sorted_fisher_processing_results,
        processing_time,
        db_species,
        original_notation,
        id_conversion,
        original_to_clean_genes):
    """
    :type id_conversion: ToEntrezConversion | ToEntrezOrthologyConversion
    :type sorted_fisher_processing_results: list of FisherCalculationResult
    :type processing_time: float
    :type db_species: str
    :type original_notation: str
    :type original_to_clean_genes: dict[str, str]
    :rtype: dict
    """
    results = []
    for i, r in enumerate(sorted_fisher_processing_results):
        results.append(fisher_process_result_to_json(db_species, r, i + 1))

    return {
        'rows': results,
        'time': processing_time,
        'total_found': len(results),
        'id_conversion': id_conversion_to_response(original_notation, id_conversion, original_to_clean_genes),
    }


def fisher_process_result_to_json(species, result, rank):
    """
    :type species: str
    :type rank: int
    :type result: FisherCalculationResult
    :rtype: dict
    """
    return {
        'title': ModuleDescription.get_title_or_default(result.gse, 'No title'),
        'rank': rank,
        'series': result.gse,
        'platform': result.gpl,
        'module_number': result.module_number,
        'series_url': get_module_heat_map_url(species, result.gse, result.gpl, result.module_number),
        'gmt_url': get_gmt_url(species, result.gse, result.gpl),
        'log_p_value': max(result.log_pvalue, -325),
        'log_adj_p_value': max(result.log_adj_p_value, -325),
        'overlap_size': result.intersection_size,
        'module_size': result.module_size,
    }


def calculate_fisher_process_results(species, entrez_query):
    """
    :type entrez_query: list of int
    :type species: str
    :rtype: list of FisherCalculationResult
    :returns sorted results
    """
    try:
        LOG.info('Trying REST service first')
        # Already sorted on back-end
        return calculate_fisher_p_values_via_rest(species, entrez_query)
    except Exception:
        LOG.exception("Can't access REST service")

    LOG.info('Calculate using data from DB.')
    results = calculate_fisher_p_values(species, GQModule.objects.filter(species=species), entrez_query)
    return sorted(results)


def query_rest(species, query_entrez_ids):
    """
    :type query_entrez_ids: list of int
    :type species: str
    :rtype str
    """
    params = {
        'species': species,
        'genes': ' '.join(map(str, query_entrez_ids)),
    }
    encoded_params = urllib.urlencode(params)
    url = 'http://{}:{}/{}'.format(settings.REST_HOST, settings.REST_PORT, settings.REST_URI)
    request = urllib2.Request(url, encoded_params)
    return urllib2.urlopen(request).read()


def calculate_fisher_p_values_via_rest(species, query_entrez_ids):
    """
    :type query_entrez_ids: list of int
    :type species: str
    :rtype list of FisherCalculationResult
    """
    # from genequery.utils.test import get_test_rest_response
    # response = json.loads(get_test_rest_response(species))

    response = json.loads(query_rest(species, query_entrez_ids))

    results = []
    for row in response:
        results.append(FisherCalculationResult(
            gse=row['gse'],
            gpl=row['gpl'],
            module_number=row['moduleNumber'],
            module_size=row['moduleSize'],
            intersection_size=row['intersectionSize'],
            species=species,
            log10_pvalue=row['logPvalue'],
        ))

    return results


class GetOverlapView(View):
    @log_get(LOG)
    def get(self, request):
        if not request.is_ajax():
            LOG.warning('Must be AJAX.')
            return JsonErrorResponse('Method not allowed', status_code=405)

        form = SearchQueryForm(request.GET)
        if not form.is_valid():
            message = '\n'.join(form.get_error_messages_as_list())
            LOG.info('Invalid form data: {}'.format(message))
            return JsonResponse({'error': message})

        original_notation = form.get_genes_id_type()
        query_species = form.cleaned_data['query_species']
        db_species = form.cleaned_data['db_species']
        input_genes = list(set(form.get_original_to_clean_genes_dict().values()))
        full_module_name = request.GET['module']

        LOG.info('GET overlap: type={}, query_species={}, db_species={}, module={}, genes={}'.format(
            original_notation, query_species, db_species, full_module_name, input_genes,
        ))

        module_genes_entrez = GQModule.objects.get(species=db_species, full_name=full_module_name).entrez_ids

        if query_species == db_species:
            id_conversion = ToEntrezConversion.convert(db_species, original_notation, input_genes)
        else:
            id_conversion = ToEntrezOrthologyConversion.convert(
                query_species, db_species, original_notation, input_genes)

        intersection = list(set(module_genes_entrez) & set(id_conversion.get_final_entrez_ids()))

        symbol_result = ToSymbolConversion.convert(db_species, 'entrez', intersection)

        return JsonResponse({'genes': symbol_result.get_final_symbol_ids(),
                             'failed': []})  # TODO remove this param


get_overlap = GetOverlapView.as_view()