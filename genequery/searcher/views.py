import logging
import os
from time import time

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.html import format_html
from django.views.generic import View

from genequery.main.views import BaseTemplateView
from genequery.searcher.forms import SearchQueryForm, OverlapQueryForm
from genequery.searcher.restapi import RestApiProxyMethods, PerformEnrichmentRestMethod, NetworkClusteringGroup
from genequery.utils import log_get, gene_list_pprint, here, require_ajax

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
    if errors:
        return JsonResponse({
            'success': False,
            'errors': errors,
            'result': None
        })
    return json_response_unknown_error()


def json_response_system_error():
    return JsonResponse({
        'success': False,
        'errors': ['System error'],
        'result': None
    })


def json_response_unknown_error():
    return JsonResponse({
        'success': False,
        'errors': ['Unknown error'],
        'result': None
    })


def handle_not_valid_search_form(search_query_form):
    if not search_query_form.is_valid():
        LOG.info('Invalid form data: {}'.format(search_query_form.get_error_messages_as_list()))
        return json_response_errors(search_query_form.get_error_messages_as_list())


class SearchProcessorView(View):
    @log_get(LOG)
    @require_ajax
    def post(self, request):
        form = SearchQueryForm(request.POST)
        if not form.is_valid():
            return handle_not_valid_search_form(form)

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

        if not result_wrapper.success:
            return json_response_errors(result_wrapper.errors)

        result = result_wrapper.result
        LOG.info('Found {} enriched items in {} sec'.format(len(result.enrichment_result_items), processing_time))

        return json_response_ok(prepare_json_data(result, species_from, species_to))


search_processor_view = SearchProcessorView.as_view()


def prepare_json_data(response_result, species_from, species_to):
    """
    :type response_result: PerformEnrichmentRestMethod.Result
    :type species_from: str
    :type species_to: str
    :rtype: dict
    """
    results = {}
    for rank, enriched_item in enumerate(response_result.enrichment_result_items):
        result_id = '{}_{}#{}'.format(enriched_item.gse, enriched_item.gpl, enriched_item.module_number)
        results[result_id] = {
            'title': response_result.gse_to_title[enriched_item.gse],
            'rank': rank + 1,
            'series': enriched_item.gse,
            'platform': enriched_item.gpl,
            'module_number': enriched_item.module_number,
            'series_url': get_module_heat_map_url(species_to,
                                                  enriched_item.gse,
                                                  enriched_item.gpl,
                                                  enriched_item.module_number),
            'gmt_url': get_gmt_url(species_to, enriched_item.gse, enriched_item.gpl),
            'log_p_value': enriched_item.log_pvalue,
            'log_adj_p_value': enriched_item.log_adj_p_value,
            'overlap_size': enriched_item.intersection_size,
            'module_size': enriched_item.module_size,
        }

    id_conversion = {
        'identified_gene_format': response_result.identified_gene_format,
        'orthology_used': species_from != species_to,
        'input_genes_to_final_entrez': response_result.gene_conversion_map

    }

    network_clustering = None
    if response_result.network_clustering_groups is not None:
        network_clustering_groups = []
        free_group = None
        for group in response_result.network_clustering_groups.values():
            group_data = {'module_names': group.module_names, 'annotation': group.annotation, 'group_id': group.group_id,
                          'score': group.score}
            if group.group_id != NetworkClusteringGroup.FREE_CLUSTER_ID:
                network_clustering_groups.append(group_data)
            else:
                free_group = group_data
        network_clustering = {'free_group': free_group, 'other_groups': network_clustering_groups}

    return {
        'enriched_modules': results,
        'id_conversion': id_conversion,
        'network_clustering': network_clustering
    }


class GetOverlapView(View):
    @log_get(LOG)
    @require_ajax
    def post(self, request):
        form = OverlapQueryForm(request.POST)
        if not form.is_valid():
            return handle_not_valid_search_form(form)

        species_from = form.cleaned_data['query_species']
        species_to = form.cleaned_data['db_species']
        raw_genes = form.cleaned_data['genes']
        full_module_name = form.cleaned_data['module']

        LOG.info('GET overlap: species_from={}, species_to={}, module={}, genes={}'.format(
            species_from, species_to, full_module_name, gene_list_pprint(raw_genes),
        ))

        result_wrapper = RestApiProxyMethods.overlap_genes_with_module.call(
            raw_genes, species_from, species_to, full_module_name)
        if not result_wrapper.success:
            return json_response_errors(result_wrapper.errors)

        return json_response_ok({
            'genes': result_wrapper.result.overlap_symbol_genes
        })


get_overlap = GetOverlapView.as_view()