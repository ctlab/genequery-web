import logging
from time import time, sleep
import urllib
import urllib2
import xmlrpclib

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import JsonResponse, HttpResponseServerError
from django.utils.html import format_html
from django.views.generic import View
from algo.fisher_empirical import fisher_empirical_p_values
from datasources.modulegenes import ModuleGenesDataSource, ModuleGenesChunkDataSource

from searcher.forms import SearchQueryForm
from searcher.models import IdMap, ModuleDescription, ModuleGenes
from utils import get_module_heat_map_url, log_get, get_gmt_url, gene_list_pprint
from utils.constants import ENTREZ, SYMBOL, INF
from utils.mixins import BaseTemplateView


LOG = logging.getLogger('genequery')

HTML_NEG_INF = format_html('-&infin;')

# TODO remove with_original_type later
def convert_to_entrez(species, genes, original_type, with_original_type=False):
    if original_type == ENTREZ:
        return list(set(map(int, genes)))
    genes_set = set(map(lambda x: x.upper(), genes))
    if original_type == SYMBOL:
        kwargs = {'symbol_id__in': genes_set}
    else:
        kwargs = {'refseq_id__in': genes_set}
    if not with_original_type:
        return list(set(IdMap.objects.filter(species=species).filter(**kwargs).values_list('entrez_id', flat=True)))
    return list(set(IdMap.objects.filter(species=species).filter(**kwargs).values_list(
        'entrez_id', original_type + '_id')))


class SearchProcessorView(View):
    @log_get(LOG)
    def get(self, request):
        if not request.is_ajax():
            LOG.warning("Not ajax request.")
            return self.http_method_not_allowed(request)
        # sleep(2);
        # return JsonResponse({'error': "adsf"})
        form = SearchQueryForm(request.GET)
        if not form.is_valid():
            message = '\n'.join(form.get_error_messages_as_list())
            LOG.info("Invalid form data: {}".format(message))
            return JsonResponse({'error': message})

        genes_id_type = form.get_genes_id_type()
        species = form.cleaned_data['species']
        genes = form.cleaned_data['genes']
        LOG.info('get request: genes {}, species {}, query type: '.format(
            gene_list_pprint(genes), species, genes_id_type))
        start_time = time()
        entrez_ids = convert_to_entrez(species, genes, genes_id_type)

        try:
            p_values = calculate_fisher_p_values(species, entrez_ids)
        except:
            message = 'Error while calculating p-values'
            LOG.exception(message)
            return HttpResponseServerError(message)

        # sorted_p_values = sorted(p_values, key=lambda i: (i[4], i[3]))
        sorted_p_values = p_values
        max_search_result_size = getattr(settings, 'MAX_SEARCH_RESULT_SIZE', len(p_values))
        modules_with_p_value = sorted_p_values[:max_search_result_size]
        series_ids_set = set([x[0] for x in modules_with_p_value])
        titles = {e['series']: e for e in ModuleDescription.objects.filter(
            series__in=series_ids_set).values('title', 'series')}
        processing_time = round(time() - start_time, 3)

        results = []
        for i, r in enumerate(modules_with_p_value):
            result = {
                'title': titles[r[0]]['title'],  # TODO .get
                'rank': i + 1,
                'series': r[0],
                'platform': r[1],
                'module_number': r[2],
                'series_url': get_module_heat_map_url(species, r[0], r[1], r[2]),
                'gmt_url': get_gmt_url(species, r[0], r[1]),
                # 'original_score': round(r[3], 2),
                'adjusted_score': round(r[4], 2) if r[4] >= -325 else '< -325',
                'overlap_size': r[5],
                'module_size': r[6],
            }
            results.append(result)
        recap = {
            'time': processing_time,
            'genes_entered': len(genes),
            'id_format': genes_id_type,
            'unique_entrez': len(entrez_ids),
            'total': len(results),
        }
        return JsonResponse({'rows': results, 'recap': recap})


search_processor_view = SearchProcessorView.as_view()


class GetOverlapView(View):
    @log_get(LOG)
    def get(self, request):
        if not request.is_ajax():
            LOG.warning("Not ajax request.")
            return self.http_method_not_allowed(request)
        form = SearchQueryForm(request.GET)
        if not form.is_valid():
            message = '\n'.join(form.get_error_messages_as_list())
            LOG.info("Invalid form data: {}".format(message))
            return JsonResponse({'error': message})

        genes_id_type = form.get_genes_id_type()
        species = form.cleaned_data['species']
        genes = form.cleaned_data['genes']
        module_number = request.GET['module']
        module = set(ModuleGenes.objects.get(species=species, module=module_number).entrez_ids)

        result = []
        if genes_id_type == ENTREZ:
            result = list(module & set(convert_to_entrez(species, genes, genes_id_type)))
        else:
            query_entrez_ids = convert_to_entrez(species, genes, genes_id_type, with_original_type=True)
            for entrez, original in query_entrez_ids:
                if entrez in module:
                    result.append(original)

        return JsonResponse({'genes': result})


get_overlap = GetOverlapView.as_view()


def calculate_fisher_p_values(species, entrez_ids):
    try:
        return calculate_fisher_p_values_via_rest(species, entrez_ids)
    except Exception, e:
        LOG.info("Can't access REST service: {}".format(e))

    if not getattr(settings, 'RUN_ON_LOW_RAM', False):
        try:
            return calculate_fisher_p_values_via_rpc(species, entrez_ids)
        except Exception, e:
            LOG.warning("Error while processing RPC: {}. Load data from DB".format(e))
            return calculate_fisher_p_values_via_db(species, entrez_ids, low_ram=False)
    # TODO remove RAM logic
    LOG.info("Too low RAM. Loading data from DB. Chunk size is {}.".format(
        getattr(settings, 'MODULE_GENES_CHUNK_SIZE', 'default')))
    return calculate_fisher_p_values_via_db(species, entrez_ids, low_ram=True)


def calculate_fisher_p_values_via_rpc(species, entrez_ids):
    rpc = xmlrpclib.ServerProxy('http://{}:{}'.format(*settings.RPC_ADDRESS))
    response = rpc.calculate_fisher_empirical_p_values(species, entrez_ids)
    if response['result'] == 'error':
        raise Exception(response['message'])
    return response['data']


def calculate_fisher_p_values_via_rest(species, entrez_ids):
    params = {
        'species': species,
        'genes': ' '.join(map(str, entrez_ids)),
    }
    url = 'http://{}:{}/{}?{}'.format(
        settings.REST_HOST, settings.REST_PORT, settings.REST_URI, urllib.urlencode(params)
    )
    lines = [x.strip().split() for x in urllib2.urlopen(url).readlines()]
    return [(gse, gpl, int(module_num), float(logPval), float(logEmpPval), int(overlap_size), int(module_size))
            for gse, gpl, module_num, logPval, logEmpPval, overlap_size, module_size in lines]



def calculate_fisher_p_values_via_db(species, entrez_ids, low_ram=False):
    if low_ram:
        data_source = ModuleGenesChunkDataSource(species=species)
    else:
        data_source = ModuleGenesDataSource()
    return fisher_empirical_p_values(species, data_source.items(species), set(entrez_ids))


class SearchPageView(BaseTemplateView):
    template_name = 'search-new.html'
    menu_active = 'searcher'

    def get_context_data(self, **kwargs):
        context = super(SearchPageView, self).get_context_data()
        fake_result = {
            'series': 'GSE46356', 'platform': 'GPL6246', 'module_number': 4, 'rank': 222,
            'series_url': '/media/modules/GSE46356_GPL6246.png',
            'gmt_url': '/media/gmt/mm/GSE46356_GPL6246.gmt', 'adjusted_score': -123.45, 'overlap_size': 123,
            'original_score': -123.45,
            'module_size': 456, 'status': 'Public on Jan 18, 2012 ',
            'title': 'Suppressor of cytokine signaling-1 influences bacterial clearance and pathology during the infection with Mycobacterium tuberculosis',
            'summary': 'Tuberculosis results from an interaction between a chronically persistent pathogen counteracted by IFN-g-mediated immune responses. '
                       'Modulation of IFN-g signaling could therefore constitute a major immune evasion mechanism for M. tuberculosis. SOCS1 plays a major '
                       'role in the inhibition of IFN-g-mediated responses. We found that M. tuberculosis infection stimulates SOCS1 expression in mouse and '
                       'human myeloid cells. Significantly higher levels of SOCS1 were induced after in vitro or in vivo infection with virulent M. ',
            'overall_design': 'Relative gene expressions were determined by normalized intensity values. GeneSpring analysis was performed using the '
                              'Treg transcriptome data with following comparisons: no GvHD d90 versus no GvHD d150, no GvHD d90 versus acute GvHD, no GvHD '}
        context['fake_result'] = fake_result
        context['request_url'] = reverse('searcher:search')
        return context


search_page_view = SearchPageView.as_view()