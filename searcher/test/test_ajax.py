import json

from django.core.urlresolvers import reverse
from django.test import Client

from searcher.forms import GENE_LIST_REQUIRED, SPECIES_REQUIRED
from searcher.views import HTML_NEG_INF
from utils.test import GQTestCase, SharedFixtureTestCase


def get_json(response):
    return json.loads(response.content)


REFSEQ_MM = "AK075969.1 AK029128.1 BC117801.1 AK148496.1 AK077787.1 AK161928.1 DN176017.1 BY154310.1 AK198132.1 " \
            "AK156158.1 AK219948.1 NM_001042615 BC013651.1 BC054821.1 X81632.1 BC047931.1 AK215112.1 AK137693.1 " \
            "AK179967.1 AK190314.1 AK191321.1 AK159327.1 AK149676.1 AK197414.1 AK032245.1 AF176521.1 AK161597.1 " \
            "AK036751.1 AK208767.1 NM_007516 AK186394.1 AK150210.1 AK211829.1 NR_075078 AK083256.1 BC024612.1 " \
            "AK180523.1 BC141393.1 BC023680.1 AK215316.1 AK171312.1 NM_025437 BC011329.1 AK197110.1 AK214983.1 L10613.1 " \
            "AK200998.1"


SYMBOL_MM = "Cd274 Nos2 Irg1 Gbp2 Cxcl9 Ptgs2 Saa3 Gbp5 Iigp1 Gbp4 Gbp3 Il1rn Il1b Oasl1 Gbp6 Cd86 Rsad2 Ccl5 Tgtp2 " \
            "Clic5 Zbp1 Gbp7 Socs3 Serpina3g Procr Igtp Slco3a1 Ly6a Slc7a2 C3 Cd40 Ifit1 Fam26f Clec4e Bst1 Isg15 Irf1 " \
            "Acsl1 Cd38 Ifit2 Thbs1 Ifi47 Ifi44 Irgm2 Il15ra Ass1 Slfn1 Nod Il18bp Serpinb9"


class QueryFormErrorTestCase(GQTestCase):
    client = Client()
    url = reverse('searcher:search')

    def test_no_form_data(self):
        response = self.send_ajax(self.url)
        data = get_json(response)
        self.assertTrue(GENE_LIST_REQUIRED in data['error'])
        self.assertTrue(SPECIES_REQUIRED in data['error'])

    def test_no_species(self):
        response = self.send_ajax(self.url, data={'genes': [1, 2, 3]})
        data = get_json(response)
        self.assertFalse(GENE_LIST_REQUIRED in data['error'])
        self.assertTrue(SPECIES_REQUIRED in data['error'])

    def test_no_genes(self):
        response = self.send_ajax(self.url, data={'species': 'mm'})
        data = get_json(response)
        self.assertTrue(GENE_LIST_REQUIRED in data['error'])
        self.assertFalse(SPECIES_REQUIRED in data['error'])

    def test_unknown_species(self):
        response = self.send_ajax(self.url, data={'species': 'sh'})
        self.assertAllIn('error', 'sh', response.content)

    def test_genes_mixed_type(self):
        response = self.send_ajax(self.url, data={'species': 'mm', 'genes': ['12345 NMP_1234.5 ASDF']})
        data = get_json(response)
        self.assertTrue("error" in data and 'same' in data['error'])

    def test_gene_too_long(self):
        response = self.send_ajax(self.url, data={'species': 'mm',
                                                  'genes': ['aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa']})
        data = get_json(response)
        self.assertTrue("error" in data and 'too long' in data['error'])

    def test_http_not_allowed(self):
        response = self.client.get(self.url, data={'some': 'data'})
        self.assertEqual(response.status_code, 405)


class QueryBaseTestCase(SharedFixtureTestCase):
    client = Client()
    url = reverse('searcher:search')

    fixtures = [
        'test_data/id_map_hs.json',
        'test_data/id_map_mm.json',
        'test_data/module_description.json',
        'test_data/module_genes_hs.json',
        'test_data/module_genes_mm.json',
    ]

    def test_entrez_hs(self):
        genes = [80218, 79718, 79624, 64853, 57665, 55795, 55699, 55251, 55146, 54407, 54107, 53339, 51714, 51696,
                 51571, 51510, 51184, 51170, 51018, 28972, 27072, 27068, 25972, 25874, 23741, 23554, 23394, 23064]
        response = self.send_ajax(
            self.url,
            data={'species': 'hs',
                  'genes': ' '.join(map(str, genes))})
        data = get_json(response)
        self.assertAllIn('Entered 28', '28 unique Entrez', '8 modules', data['recap'])
        self.assertIn(HTML_NEG_INF, data['data'][0])

    def test_entrez_mm(self):
        genes = [384763, 382030, 381760, 381510, 380664, 378702, 330544, 328110, 320910, 320873, 320560, 320184, 320105,
                 320024, 319880, 319211, 271457, 270669, 269774, 246316, 245404, 244349, 243780, 242362, 240396]
        response = self.send_ajax(
            self.url,
            data={'species': 'mm',
                  'genes': ' '.join(map(str, genes))})
        data = get_json(response)
        self.assertAllIn('Entered 25', '25 unique Entrez', '3 modules', data['recap'])
        self.assertIn('GSE10202', data['data'][0])

    def test_refseq_mm(self):
        response = self.send_ajax(
            self.url,
            data={'species': 'mm',
                  'genes': REFSEQ_MM})
        data = get_json(response)
        self.assertAllIn('Entered 47', '1 unique Entrez', '0 modules', data['recap'])

    def test_symbol_mm(self):
        response = self.send_ajax(
            self.url,
            data={'species': 'mm',
                  'genes': SYMBOL_MM})
        data = get_json(response)
        self.assertAllIn('Entered 50', '13 unique Entrez', '7 modules', data['recap'])
        self.assertIn('GSE26695', data['data'][0])

    def test_filter_unique_entrez(self):
        genes = [384763, 382030, 381760, 381510, 380664, 378702, 330544, 328110, 320910, 320873, 320560, 320184, 320105,
                 384763, 382030, 381760, 381510, 380664, 378702, 330544, 328110, 320910, 320873, 320560, 320184, 320105]
        response = self.send_ajax(
            self.url,
            data={'species': 'mm',
                  'genes': ' '.join(map(str, genes))})
        data = get_json(response)
        self.assertAllIn('Entered 26', '13 unique Entrez', '3 modules', data['recap'])
        self.assertIn('GSE10202', data['data'][0])