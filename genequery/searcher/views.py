import logging
import os
import json
from time import time
import urllib
import urllib2
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import JsonResponse, HttpResponseServerError
from django.utils.html import format_html
from django.views.generic import View

from genequery.utils.constants import MIN_LOG_EMPIRICAL_P_VALUE, INF
from genequery.utils.test import get_test_rest_response
from math.fisher_empirical import FisherCalculationResult, fisher_empirical_p_values
from genequery.main.views import BaseTemplateView
from genequery.searcher.forms import SearchQueryForm
from genequery.searcher.models import IdMap, ModuleDescription, GQModule
from genequery.utils import log_get, gene_list_pprint, here

LOG = logging.getLogger('genequery')

HTML_NEG_INF = format_html('-&infin;')


def get_module_heat_map_url(species, gse, gpl, module_number):
    """
    :type module_number: int
    :type gpl: str
    :type gse: str
    :type species: str
    :rtype: str
    """
    path_to_image = here('modules', species, '{}_{}_module_{}.svg'.format(gse, gpl, module_number))
    path = here(settings.MEDIA_ROOT, path_to_image)
    return here(settings.MEDIA_URL, path_to_image) if os.path.exists(path) else None


def get_gmt_url(species, gse, gpl):
    """
    :type species: str
    :type gpl: str
    :type gse: str
    """
    path_to_file = here('gmt', species, '{}_{}.gmt'.format(gse, gpl))
    path = here(settings.MEDIA_ROOT, path_to_file)
    return here(settings.MEDIA_URL, path_to_file) if os.path.exists(path) else None


class SearchPageView(BaseTemplateView):
    template_name = 'search.html'
    menu_active = 'searcher'

    def get_context_data(self, **kwargs):
        context = super(SearchPageView, self).get_context_data()
        context['request_url'] = reverse('searcher:search')
        return context


search_page_view = SearchPageView.as_view()


class SearchProcessorView(View):
    @log_get(LOG)
    def get(self, request):
        if not request.is_ajax():
            LOG.warning('Not ajax request.')
            return self.http_method_not_allowed(request)

        form = SearchQueryForm(request.GET)
        if not form.is_valid():
            message = '\n'.join(form.get_error_messages_as_list())
            LOG.info('Invalid form data: {}'.format(message))
            return JsonResponse({'error': message})

        input_genes_notation_type = form.get_genes_id_type()
        species = form.cleaned_data['species']

        genes = form.cleaned_data['genes']  # list of str
        LOG.info('GET request: genes {}, species {}, query type: {}.'.format(
            gene_list_pprint(genes), species, input_genes_notation_type))

        start_time = time()

        entrez_to_original = IdMap.convert_to_entrez(species, input_genes_notation_type, genes)

        if not entrez_to_original:
            return build_search_result_data(
                [],
                0,
                species,
                len(genes),
                input_genes_notation_type,
                len(entrez_to_original),
            )

        try:
            sorted_results = calculate_fisher_process_results(species, [pair[0] for pair in entrez_to_original])
        except:
            message = 'Error while calculating p-values'
            LOG.exception(message)
            return HttpResponseServerError(message)

        processing_time = round(time() - start_time, 3)

        return build_search_result_data(
            sorted_results,
            processing_time,
            species,
            len(genes),
            input_genes_notation_type,
            len(entrez_to_original),
        )


search_processor_view = SearchProcessorView.as_view()


def build_search_result_data(
        sorted_fisher_processing_results,
        processing_time,
        species,
        original_genes_count,
        original_notation,
        unique_entrez_count):
    results = []
    for i, r in enumerate(sorted_fisher_processing_results):
        results.append(fisher_process_result_to_json(species, r, i + 1))

    recap = {
        'time': processing_time,
        'genes_entered': original_genes_count,
        'id_format': original_notation,
        'unique_entrez': unique_entrez_count,
        'total': len(results),
    }
    return JsonResponse({'rows': results, 'recap': recap})


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
        'adjusted_score': round(result.log_emp_pvalue, 2) if result.log_emp_pvalue != -INF
                                                          else '< {}'.format(MIN_LOG_EMPIRICAL_P_VALUE),
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
        LOG.exception("Can't access REST service: {}")

    LOG.info('Calculate using data from DB.')
    results = fisher_empirical_p_values(species, GQModule.objects.filter(species=species), entrez_query)
    return sorted(results)


def calculate_fisher_p_values_via_rest(species, query_entrez):
    """
    :type query_entrez: list of int
    :type species: str
    :rtype list of FisherCalculationResult
    """
    params = {
        'species': species,
        'genes': ' '.join(map(str, query_entrez)),
    }
    url = 'http://{}:{}/{}?{}'.format(
        settings.REST_HOST, settings.REST_PORT, settings.REST_URI, urllib.urlencode(params)
    )

    # LOG.warn('User fake response!')
    # # sleep(3)
    # response = json.loads(get_test_rest_response(species))

    response = json.loads(urllib2.urlopen(url).read())

    results = []
    for row in response:
        results.append(FisherCalculationResult(
            gse=row['gse'],
            gpl=row['gpl'],
            module_number=row['moduleNumber'],
            module_size=row['moduleSize'],
            intersection_size=row['intersectionSize'],
            log10_pvalue=row['logPvalue'],
            log10_emp_pvalue=row['logEmpiricalPvalue'],
        ))

    return results


class GetOverlapView(View):
    @log_get(LOG)
    def get(self, request):
        if not request.is_ajax():
            LOG.warning('Not ajax request.')
            return self.http_method_not_allowed(request)

        form = SearchQueryForm(request.GET)
        if not form.is_valid():
            message = '\n'.join(form.get_error_messages_as_list())
            LOG.info('Invalid form data: {}'.format(message))
            return JsonResponse({'error': message})

        genes_id_type = form.get_genes_id_type()
        species = form.cleaned_data['species']
        genes = form.cleaned_data['genes']
        full_module_name = request.GET['module']

        LOG.info('GET overlap: type={}, species={}, module={}, genes={}'.format(
            genes_id_type, species, full_module_name, genes,
        ))

        result = []
        entrez_genes = GQModule.objects.get(species=species, full_name=full_module_name).entrez_ids
        for entrez, original in IdMap.convert_to_entrez(species, genes_id_type, genes):
            if entrez in entrez_genes:
                result.append(original)

        return JsonResponse({'genes': result})


get_overlap = GetOverlapView.as_view()