import json
from mock import patch

from django.core.urlresolvers import reverse
from django.test import Client

from genequery.searcher.forms import GENE_LIST_REQUIRED, QUERY_SPECIES_REQUIRED, DB_SPECIES_REQUIRED, MODULE_REQUIRED
from genequery.searcher.restapi import RestResponseWrapperProxy
from genequery.utils.test import GQTestCase


def get_json(response):
    return json.loads(response.content)


class GetOverlapTestCase(GQTestCase):
    client = Client()
    url = reverse('searcher:get_overlap')

    return_value = RestResponseWrapperProxy({
        "result": {
            "overlapSymbolGenes": [
                "C1ORF216",
                "POTEKP"
            ]
        },
        "success": True,
        "errors": None
    })

    @patch('genequery.searcher.restapi.OverlapGenesWithModuleRestMethod._make_request', return_value=return_value)
    def test_full_form(self, mocked_response):
        response = self.send_post(self.url,
                                  data={'db_species': 'hs',
                                        'query_species': 'hs',
                                        'module': 'GSE1000_GPL96#0',
                                        'genes': '440915 127703'})
        data = get_json(response)
        self.assertTrue(data['success'])
        self.assertTrue('genes' in data['result'])
        self.assertIsNone(data['errors'])

    @patch('genequery.searcher.restapi.OverlapGenesWithModuleRestMethod._make_request', return_value=return_value)
    def test_no_form_data(self, mocked_response):
        response = self.send_post(self.url)
        data = get_json(response)
        self.assertFalse(data['success'])
        self.assertIsNone(data['result'])
        self.assertTrue(DB_SPECIES_REQUIRED in data['errors'])
        self.assertTrue(QUERY_SPECIES_REQUIRED in data['errors'])
        self.assertTrue(MODULE_REQUIRED in data['errors'])
        self.assertTrue(GENE_LIST_REQUIRED in data['errors'])

    @patch('genequery.searcher.restapi.OverlapGenesWithModuleRestMethod._make_request', return_value=return_value)
    def test_no_species_and_module(self, mocked_response):
        response = self.send_post(self.url, data={'genes': '1 2 3'})
        data = get_json(response)
        self.assertFalse(data['success'])
        self.assertIsNone(data['result'])
        self.assertTrue(DB_SPECIES_REQUIRED in data['errors'])
        self.assertTrue(QUERY_SPECIES_REQUIRED in data['errors'])
        self.assertTrue(MODULE_REQUIRED in data['errors'])

    @patch('genequery.searcher.restapi.OverlapGenesWithModuleRestMethod._make_request', return_value=return_value)
    def test_no_genes_and_module(self, mocked_response):
        response = self.send_post(self.url,
                                  data={'db_species': 'hs',
                                        'query_species': 'hs'})
        data = get_json(response)
        self.assertFalse(data['success'])
        self.assertIsNone(data['result'])
        self.assertTrue(GENE_LIST_REQUIRED in data['errors'])
        self.assertTrue(MODULE_REQUIRED in data['errors'])

    @patch('genequery.searcher.restapi.OverlapGenesWithModuleRestMethod._make_request', return_value=return_value)
    def test_no_module(self, mocked_response):
        response = self.send_post(self.url,
                                  data={'db_species': 'hs',
                                        'query_species': 'hs',
                                        'genes': "440915 127703"})
        data = get_json(response)
        self.assertFalse(data['success'])
        self.assertIsNone(data['result'])
        self.assertTrue(MODULE_REQUIRED in data['errors'])

    @patch('genequery.searcher.restapi.OverlapGenesWithModuleRestMethod._make_request', return_value=return_value)
    def test_unknown_species(self, mocked_response):
        response = self.send_post(self.url,
                                  data={'db_species': 'gg',
                                        'query_species': 'wp',
                                        'module': 'GSE1000_GPL96#0',
                                        'genes': '440915 127703'})
        data = get_json(response)
        self.assertFalse(data['success'])
        self.assertIsNone(data['result'])
        self.assertTrue(any('gg' in x for x in data['errors']))
        self.assertTrue(any('wp' in x for x in data['errors']))


class SearchProcessorTestCase(GQTestCase):
    client = Client()
    url = reverse('searcher:search')

    return_value = RestResponseWrapperProxy({
        "result": {
            "identifiedGeneFormat": "entrez",
            "geneConversionMap": {
                "11137": 11137,
                "11345": None,
                "23014": 23014,
                "24137": 24137,
                "25939": 25939,
                "27089": 27089,
                "29978": 29978,
                "51121": 51121,
                "51227": 51227,
                "51637": 51637,
                "55179": 55179,
                "55333": 55333,
                "64105": 64105,
                "64963": 64963,
                "79665": 79665,
                "80213": 80213,
                "80762": 80762,
                "91942": 91942,
                "91947": 91947,
                "112495": 112495,
                "139341": 139341,
                "153527": 153527,
                "375444": 375444,
                "390916": 390916,
                "494143": 494143
            },
            "gseToTitle": {
                "GSE10021": "Some gse.",
                "GSE100219": "Another gse."
            },
            "enrichmentResultItems": [
                {
                    "gse": 10021,
                    "gpl": 570,
                    "moduleNumber": 30,
                    "pvalue": 1.7704e-60,
                    "logPvalue": -53.752016282686824,
                    "adjPvalue": 8.8502e-52,
                    "logAdjPvalue": -51.053046278350806,
                    "intersectionSize": 25,
                    "moduleSize": 55
                },
                {
                    "gse": 100219,
                    "gpl": 555,
                    "moduleNumber": 42,
                    "pvalue": 1.7704e-50,
                    "logPvalue": -43.752016282686824,
                    "adjPvalue": 8.8502e-42,
                    "logAdjPvalue": -41.053046278350806,
                    "intersectionSize": 22,
                    "moduleSize": 44
                }
            ]
        },
        "success": True,
        "errors": None
    })

    @patch('genequery.searcher.restapi.PerformEnrichmentRestMethod._make_request', return_value=return_value)
    def test_full_form(self, mocked_response):
        response = self.send_post(self.url,
                                  data={'db_species': 'hs',
                                        'query_species': 'hs',
                                        'genes': '494143 390916 375444 153527 139341 112495 91947 91942 80762 80213 \
                                        79665 64963 64105 55333 55179 51637 51227 51121 29978 27089 25939 24137 23014 \
                                        11345 11137'})
        data = get_json(response)
        self.assertTrue(data['success'])
        self.assertIsNone(data['errors'])
        self.assertEqual(len(data['result']['enriched_modules']), 2)

        self.assertIn('title', data['result']['enriched_modules'][0])
        self.assertIn('gmt_url', data['result']['enriched_modules'][0])
        self.assertIn('series', data['result']['enriched_modules'][0])
        self.assertIn('module_number', data['result']['enriched_modules'][0])
        self.assertIn('rank', data['result']['enriched_modules'][0])
        self.assertIn('platform', data['result']['enriched_modules'][0])
        self.assertIn('log_adj_p_value', data['result']['enriched_modules'][0])
        self.assertIn('series_url', data['result']['enriched_modules'][0])
        self.assertIn('log_p_value', data['result']['enriched_modules'][0])

        self.assertIn('identified_gene_format', data['result']['id_conversion'])
        self.assertIn('orthology_used', data['result']['id_conversion'])
        self.assertIn('input_genes_to_final_entrez', data['result']['id_conversion'])

    @patch('genequery.searcher.restapi.PerformEnrichmentRestMethod._make_request', return_value=return_value)
    def test_no_form_data(self, mocked_response):
        response = self.send_post(self.url)
        data = get_json(response)
        self.assertFalse(data['success'])
        self.assertIsNone(data['result'])
        self.assertTrue(DB_SPECIES_REQUIRED in data['errors'])
        self.assertTrue(QUERY_SPECIES_REQUIRED in data['errors'])
        self.assertTrue(GENE_LIST_REQUIRED in data['errors'])

    @patch('genequery.searcher.restapi.PerformEnrichmentRestMethod._make_request', return_value=return_value)
    def test_no_species(self, mocked_response):
        response = self.send_post(self.url, data={'genes': '1 2 3'})
        data = get_json(response)
        self.assertFalse(data['success'])
        self.assertIsNone(data['result'])
        self.assertTrue(DB_SPECIES_REQUIRED in data['errors'])
        self.assertTrue(QUERY_SPECIES_REQUIRED in data['errors'])

    @patch('genequery.searcher.restapi.PerformEnrichmentRestMethod._make_request', return_value=return_value)
    def test_no_genes(self, mocked_response):
        response = self.send_post(self.url,
                                  data={'db_species': 'hs',
                                        'query_species': 'hs'})
        data = get_json(response)
        self.assertFalse(data['success'])
        self.assertIsNone(data['result'])
        self.assertTrue(GENE_LIST_REQUIRED in data['errors'])

    @patch('genequery.searcher.restapi.PerformEnrichmentRestMethod._make_request', return_value=return_value)
    def test_unknown_species(self, mocked_response):
        response = self.send_post(self.url,
                                  data={'db_species': 'gg',
                                        'query_species': 'wp',
                                        'genes': '440915 127703'})
        data = get_json(response)
        self.assertFalse(data['success'])
        self.assertIsNone(data['result'])
        self.assertTrue(any('gg' in x for x in data['errors']))
        self.assertTrue(any('wp' in x for x in data['errors']))
