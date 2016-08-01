import json
import urllib2

from django.conf import settings

from genequery.searcher.gea import EnrichmentResultItem


class RestResponseWrapperProxy:
    def __init__(self, rest_response):
        """
        Wrapper for raw REST API response

        :type rest_response: dict
        """
        self.errors = rest_response['errors']
        self.success = rest_response['success']
        self.raw_result = rest_response['result']


class AbstractRestProxyMethod:

    class Result:
        """
        Typed version of the `result` field of the REST API response.
        """
        pass

    class ResultWrapper:
        """
        Wrapper for raw REST API response with typed `result` field.
        """
        pass

    _url = None

    def get_url(self):
        return self._url

    def call(self, *args, **kwargs):
        raise NotImplementedError()

    def _make_request(self, params):
        """
        :type params: dict
        :rtype: RestResponseWrapperProxy
        """
        headers = {'Content-Type': 'application/json'}
        request = urllib2.Request(
            self.get_url(),
            json.dumps(params),
            headers
        )
        try:
            resp = urllib2.urlopen(request)
        except urllib2.HTTPError, error:
            if error.getcode() == 400:
                resp = error
            else:
                raise error
        return RestResponseWrapperProxy(json.loads(resp.read()))


class PerformEnrichmentRestMethod(AbstractRestProxyMethod):

    class Result(AbstractRestProxyMethod.Result):
        def __init__(self, response_result_data, species_to):
            """
            :type response_result_data: dict
            :type species_to: str
            """
            if response_result_data is None:
                raise Exception('response result must be non-null')

            self.gene_conversion_map = response_result_data['geneConversionMap']
            self.identified_gene_format = response_result_data['identifiedGeneFormat']
            self.enrichment_result_items = []
            for enriched_item in response_result_data['enrichmentResultItems']:
                self.enrichment_result_items.append(EnrichmentResultItem(
                    gse='GSE{}'.format(enriched_item['gse']),
                    gpl='GPL{}'.format(enriched_item['gpl']),
                    module_number=enriched_item['moduleNumber'],
                    module_size=enriched_item['moduleSize'],
                    intersection_size=enriched_item['intersectionSize'],
                    species=species_to,
                    pvalue=enriched_item['pvalue'],
                    log10_pvalue=enriched_item['logPvalue'],
                    adj_pvalue=enriched_item['adjPvalue'],
                    log10_adj_pvalue=enriched_item['logAdjPvalue'],
                ))
            self.gse_to_title = response_result_data['gseToTitle']

    class ResultWrapper(AbstractRestProxyMethod.ResultWrapper):
        def __init__(self, success, result, errors):
            """
            :type success: bool
            :type result: PerformEnrichmentRestMethod.Result or None
            :type errors: list[str] or None
            """
            self.success = success
            self.result = result
            self.errors = errors

    _url = 'http://{}:{}/{}'.format(settings.NEW_REST_HOST, settings.NEW_REST_PORT, 'perform-enrichment')

    def call(self, genes, species_from, species_to):
        """
        :type genes: iterable[str]
        :type species_from: str
        :type species_to: str

        :returns: (success, result payload, errors)
        :rtype: PerformEnrichmentRestMethod.ResultWrapper
        """
        params = {
            'genes': genes,
            'speciesFrom': species_from,
            'speciesTo': species_to,
        }
        response = self._make_request(params)
        return PerformEnrichmentRestMethod.ResultWrapper(
            response.success,
            self.Result(response.raw_result, species_to) if response.success else None,
            response.errors
        )


class OverlapGenesWithModuleRestMethod(AbstractRestProxyMethod):

    class Result(AbstractRestProxyMethod.Result):
        def __init__(self, response_result_data):
            """
            :type response_result_data: dict
            """
            if response_result_data is None:
                raise Exception('response result must be non-null')

            self.overlap_symbol_genes = response_result_data['overlapSymbolGenes']

    class ResultWrapper(AbstractRestProxyMethod.ResultWrapper):
        def __init__(self, success, result, errors):
            """
            :type success: bool
            :type result: OverlapGenesWithModuleRestMethod.Result or None
            :type errors: list[str] or None
            """
            self.success = success
            self.result = result
            self.errors = errors

    _url = 'http://{}:{}/{}'.format(settings.NEW_REST_HOST, settings.NEW_REST_PORT, 'find-overlap')

    def call(self, genes, species_from, species_to, module_name):
        """
        :type genes: iterable[str]
        :type species_from: str
        :type species_to: str
        :type module_name: str

        :returns: (success, result payload, errors)
        :rtype: OverlapGenesWithModuleRestMethod.ResultWrapper
        """
        params = {
            'genes': genes,
            'speciesFrom': species_from,
            'speciesTo': species_to,
            'moduleName': module_name,
        }
        response = self._make_request(params)
        return OverlapGenesWithModuleRestMethod.ResultWrapper(
            response.success,
            self.Result(response.raw_result) if response.success else None,
            response.errors
        )


class RestApiProxyMethods:
    perform_enrichment_method = PerformEnrichmentRestMethod()
    overlap_genes_with_module = OverlapGenesWithModuleRestMethod()
