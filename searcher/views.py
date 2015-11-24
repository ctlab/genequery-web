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

from common.constants import MIN_LOG_EMPIRICAL_P_VALUE, INF
from common.dataset import ModuleName
from common.math.fisher_empirical import FisherCalculationResult, fisher_empirical_p_values
from main.views import BaseTemplateView
from searcher.forms import SearchQueryForm
from utils import log_get, gene_list_pprint, here
from dataholder import modules_data_holder, id_mapping, gse_to_title

LOG = logging.getLogger('genequery')

HTML_NEG_INF = format_html('-&infin;')


def get_module_heat_map_url(species, module_name):
    """
    :type module_name: ModuleName
    :rtype: str
    """
    path_to_image = here('modules', species, '{}_{}_module_{}.svg'.format(
        module_name.gse, module_name.gpl, module_name.module_number))
    path = here(settings.MEDIA_ROOT, path_to_image)
    return here(settings.MEDIA_URL, path_to_image) if os.path.exists(path) else None


def get_gmt_url(species, module_name):
    """
    :type species: str
    :type module_name: ModuleName
    """
    path_to_file = here('gmt', species, '{}_{}.gmt'.format(module_name.gse, module_name.gpl))
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

        entrez_to_original = id_mapping.convert_to_entrez(species, input_genes_notation_type, genes)

        try:
            sorted_results = calculate_fisher_process_results(species, [pair[0] for pair in entrez_to_original])
        except:
            message = 'Error while calculating p-values'
            LOG.exception(message)
            return HttpResponseServerError(message)

        processing_time = round(time() - start_time, 3)

        results = []
        for i, r in enumerate(sorted_results):
            results.append(fisher_process_result_to_json(r, i + 1))

        recap = {
            'time': processing_time,
            'genes_entered': len(genes),
            'id_format': input_genes_notation_type,
            'unique_entrez': len(entrez_to_original),
            'total': len(results),
        }
        return JsonResponse({'rows': results, 'recap': recap})


search_processor_view = SearchProcessorView.as_view()


def fisher_process_result_to_json(result, rank):
    """
    :type rank: int
    :type result: FisherCalculationResult
    :rtype: dict
    """
    module = result.module
    gse = module.name.gse
    gpl = module.name.gpl
    module_number = module.name.module_number

    return {
        'title': gse_to_title.get(gse, 'No title'),
        'rank': rank,
        'series': gse,
        'platform': gpl,
        'module_number': module_number,
        'series_url': get_module_heat_map_url(module.species, module.name),
        'gmt_url': get_gmt_url(module.species, module.name),
        'adjusted_score': round(result.log_emp_pvalue, 2) if result.log_emp_pvalue != -INF
                                                          else '< {}'.format(MIN_LOG_EMPIRICAL_P_VALUE),
        'overlap_size': result.intersection_size,
        'module_size': len(module),
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

    LOG.info('Calculate request using pre-loaded data.')
    results = fisher_empirical_p_values(species, modules_data_holder.get_modules(species), entrez_query)
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

    # if is_dev_mode():
    #     LOG.warn('User fake response!')
    #     # sleep(3)
    #     response = json.loads(get_test_rest_response(species))
    # else:
    response = json.loads(urllib2.urlopen(url).read())
    results = []
    for row in response:
        results.append(FisherCalculationResult(
            module=modules_data_holder.get_module(
                species,
                ModuleName.build_full(row['gse'], row['gpl'], row['moduleNumber'])),
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
        module = modules_data_holder.get_module(species, full_module_name).gene_ids_set
        for entrez, original in id_mapping.convert_to_entrez(species, genes_id_type, genes):
            if entrez in module:
                result.append(original)

        return JsonResponse({'genes': result})


get_overlap = GetOverlapView.as_view()
