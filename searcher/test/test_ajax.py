import json
from pprint import pprint
from django.core.urlresolvers import reverse
from django.test import Client
from searcher.forms import GENE_LIST_REQUIRED, SPECIES_REQUIRED
from utils.test import GQTestCase


def get_json(response):
    return json.loads(response.content)


class QueryFormErrorTestCase(GQTestCase):
    client = Client()
    url = reverse('searcher:search')

    # def assertHasError(self, data, msg):

    def test_no_form_data(self):
        response = self.client.get(self.url, {}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assert_200(response)
        data = get_json(response)
        self.assertTrue(GENE_LIST_REQUIRED in data['error'])
        self.assertTrue(SPECIES_REQUIRED in data['error'])

    def test_no_species(self):
        response = self.client.get(self.url, {'genes': [1, 2, 3]}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assert_200(response)
        data = get_json(response)
        self.assertFalse(GENE_LIST_REQUIRED in data['error'])
        self.assertTrue(SPECIES_REQUIRED in data['error'])

    def test_no_genes(self):
        response = self.client.get(self.url, {'species': 'mm'}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assert_200(response)
        data = get_json(response)
        self.assertTrue(GENE_LIST_REQUIRED in data['error'])
        self.assertFalse(SPECIES_REQUIRED in data['error'])