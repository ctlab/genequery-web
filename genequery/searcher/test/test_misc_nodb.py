from django.test import SimpleTestCase

from genequery.searcher.idconvertion import adjust_symbol_genes


class TestMisc(SimpleTestCase):
    def test_adjust_symbol_genes_to_hs(self):
        genes = ['AA', 'Aa', 'aA', 'aa', 'a-a', '1.1-1.2', 'a1', 'A1.a']
        adjusted = adjust_symbol_genes('hs', genes)
        self.assertItemsEqual(['AA', 'AA', 'AA', 'AA', 'A-A', '1.1-1.2', 'A1', 'A1.A'], adjusted.values())

    def test_adjust_symbol_genes_to_mm_rt(self):
        genes = ['AA', 'Aa', 'aA', 'aa', 'a-a', '1.1-1.2', 'a1a', 'A1.a']
        expected = ['Aa', 'Aa', 'Aa', 'Aa', 'A-a', '1.1-1.2', 'A1a', 'A1.a']

        self.assertItemsEqual(expected, adjust_symbol_genes('mm', genes).values())
        self.assertItemsEqual(expected, adjust_symbol_genes('rt', genes).values())