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


def get_test_rest_response():
    return """GSE46356	GPL6246	4	-33.89	-191.82	39	704
GSE23508	GPL7202	2	-32.68	-176.83	38	771
GSE4066	GPL339	18	-31.01	-157.22	19	55
GSE25313	GPL6246	2	-30.38	-150.12	36	649
GSE31906	GPL6246	5	-29.42	-139.58	20	78
GSE26147	GPL6246	5	-28.49	-129.83	20	152
GSE33266	GPL4134	3	-28.45	-129.43	36	694
GSE15610	GPL1261	2	-28.43	-129.22	38	865
GSE34913	GPL8321	5	-27.82	-122.95	29	446
GSE23639	GPL4134	3	-27.33	-118.04	26	483
GSE2421	GPL339	3	-26.72	-112.14	26	370
GSE34324	GPL1261	3	-26.31	-108.22	31	408
GSE20210	GPL4134	2	-26.14	-106.62	44	1426
GSE13522	GPL1261	4	-25.77	-103.18	27	416
GSE17115	GPL8321	2	-25.50	-100.75	34	750
GSE38014	GPL7202	13	-24.97	-96.00	22	189
GSE49122	GPL1261	3	-24.26	-89.72	24	375
GSE37612	GPL6885	4	-24.17	-88.94	30	679
GSE38093	GPL8321	2	-23.75	-85.45	33	798
GSE24594	GPL8321	14	-23.48	-83.15	17	119
GSE42768	GPL6246	4	-23.34	-82.01	28	476
GSE37475	GPL8321	7	-22.86	-78.15	22	234
GSE9488	GPL81	3	-22.73	-77.12	33	813
GSE40857	GPL8321	16	-22.68	-76.71	16	73
GSE33201	GPL1261	14	-22.65	-76.46	12	59
GSE33199	GPL1261	14	-22.65	-76.46	12	59
GSE38822	GPL1261	2	-22.41	-74.59	32	828
GSE15721	GPL8321	5	-22.40	-74.46	28	405
GSE11809	GPL8321	3	-22.37	-74.23	35	885
GSE41355	GPL6885	2	-22.36	-74.14	28	637
GSE27378	GPL1261	10	-22.23	-73.13	13	52
GSE47046	GPL8321	6	-22.13	-72.37	25	275
GSE37665	GPL7202	7	-22.07	-71.96	25	406
GSE24357	GPL6887	4	-21.92	-70.78	24	414
GSE6970	GPL339	6	-21.88	-70.50	17	146"""


class SearchProcessorView(View):
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

        sorted_p_values = sorted(p_values, key=lambda i: (i[4], i[3]))
        # sorted_p_values = p_values
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
        LOG.warn("Can't access REST service: {}".format(e))

    if not getattr(settings, 'RUN_ON_LOW_RAM', False):
        try:
            return calculate_fisher_p_values_via_rpc(species, entrez_ids)
        except Exception, e:
            LOG.warning("Can't access RPC service: {}".format(e))
            LOG.info("Loading data from DB")
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

    # LOG.warn("User fake response!")
    # sleep(3)
    # lines = [x.strip().split() for x in get_test_rest_response().split("\n")]

    return [(gse, gpl, int(module_num), float(logPval), float(logEmpPval), int(overlap_size), int(module_size))
            for gse, gpl, module_num, logPval, logEmpPval, overlap_size, module_size in lines]


def calculate_fisher_p_values_via_db(species, entrez_ids, low_ram=False):
    if low_ram:
        data_source = ModuleGenesChunkDataSource(species=species)
    else:
        data_source = ModuleGenesDataSource()
    return fisher_empirical_p_values(species, data_source.items(species), set(entrez_ids))


class SearchPageView(BaseTemplateView):
    template_name = 'search.html'
    menu_active = 'searcher'

    def get_context_data(self, **kwargs):
        context = super(SearchPageView, self).get_context_data()
        context['request_url'] = reverse('searcher:search')
        return context


search_page_view = SearchPageView.as_view()
