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
from genequery.searcher.restapi import RestApiProxyMethods
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


def json_response_ok(data):
    return JsonResponse({
        'success': True,
        'errors': None,
        'result': data
    })


def json_response_errors(errors):
    return JsonResponse({
        'success': False,
        'errors': errors,
        'result': None
    })


def json_response_system_error():
    return JsonResponse({
        'success': False,
        'errors': ['System error'],
        'result': None
    })


class SearchProcessorView(View):
    @log_get(LOG)
    def post(self, request):
        if not request.is_ajax():
            LOG.warning('Search request must be AJAX.')
            return JsonErrorResponse('Method not allowed', status_code=405)

        form = SearchQueryForm(request.POST)
        if not form.is_valid():
            LOG.info('Invalid form data: {}'.format('\n'.join(form.get_error_messages_as_list())))
            return json_response_errors(form.get_error_messages_as_list())

        species_from = form.cleaned_data['query_species']
        species_to = form.cleaned_data['db_species']

        raw_genes = form.cleaned_data['genes']
        LOG.info('GET request: genes {}, query_species {}, db_species: {}.'.format(
            gene_list_pprint(raw_genes), species_from, species_to))

        try:
            start_time = time()
            result_wrapper = RestApiProxyMethods.perform_enrichment_method.call(raw_genes, species_from, species_to)
            processing_time = round(time() - start_time, 3)
        except:
            LOG.exception('Error while calculating p-values')
            return json_response_system_error()

        id_conversion = {
            'identified_gene_format': result_wrapper.result.identified_gene_format,
            'orthology_used': species_from == species_to,
            'input_genes_to_final_entrez': result_wrapper.result.gene_conversion_map

        }
        LOG.info('Found {} items in {} sec'.format(len(result_wrapper.result.enrichment_result_items), processing_time))

        return json_response_ok(build_search_result_data(
            result_wrapper.result.enrichment_result_items,
            result_wrapper.result.identified_gene_format,
            id_conversion,
        ))


search_processor_view = SearchProcessorView.as_view()


def build_search_result_data(
        enrichment_result_items,
        db_species,
        id_conversion):
    """
    :type id_conversion: dict
    :type enrichment_result_items: list[FisherCalculationResult]
    :type db_species: str
    :rtype: dict
    """
    results = []
    for i, r in enumerate(enrichment_result_items):
        results.append(enrichment_result_item_to_json(db_species, r, i + 1))

    return {
        'rows': results,
        'id_conversion': id_conversion,
    }


def enrichment_result_item_to_json(species, result, rank):
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