import json
import urllib
import urllib2

from django.conf import settings

from genequery.searcher.math.fisher_empirical import FisherCalculationResult


class RestResponseWrapperProxy:
    def __init__(self, rest_response):
        """
        :type rest_response: dict
        """
        self.errors = rest_response['errors']
        self.success = rest_response['success']
        self.raw_result = rest_response['result']


class AbstractRestProxyMethod:

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
        return RestResponseWrapperProxy(json.loads(urllib2.urlopen(request).read()))


class PerformEnrichmentRestProxyMethod(AbstractRestProxyMethod):

    class Result:
        def __init__(self, response_result_data, species_to):
            self.gene_conversion_map = response_result_data['geneConversionMap']
            self.identified_gene_format = response_result_data['identifiedGeneFormat']
            self.enrichment_result_items = []
            for enriched_item in response_result_data['enrichmentResultItems']:
                self.enrichment_result_items.append(FisherCalculationResult(
                    gse='GSE{}'.format(enriched_item['gse']),
                    gpl='GPL{}'.format(enriched_item['gpl']),
                    module_number=enriched_item['moduleNumber'],
                    module_size=enriched_item['moduleSize'],
                    intersection_size=enriched_item['intersectionSize'],
                    species=species_to,
                    log10_pvalue=enriched_item['logPvalue'],
                ))

    class ResultWrapper:
        def __init__(self, success, result, errors):
            """
            :type success: bool
            :type result: PerformEnrichmentRestProxyMethod.Result or None
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
        :rtype: PerformEnrichmentRestProxyMethod.ResultWrapper
        """
        params = {
            'genes': genes,
            'speciesFrom': species_from,
            'speciesTo': species_to,
        }
        response = self._make_request(params)
        return PerformEnrichmentRestProxyMethod.ResultWrapper(
            response.success,
            self.Result(response.raw_result, species_to),
            response.errors
        )


class RestApiProxyMethods:
    perform_enrichment_method = PerformEnrichmentRestProxyMethod()
