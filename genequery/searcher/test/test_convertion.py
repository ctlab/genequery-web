from django.test import TestCase

from genequery.searcher.idconvertion import convert_to_entrez, convert_entrez_to_symbol


class TestIDConvertion(TestCase):
    fixtures = ['symbol_to_entrez.json', 'other_to_entrez.json']

    def test_entrez(self):
        self.assertEqual(convert_to_entrez('hs', 'entrez', ['1', '2', '3']),
                         {'converted': {'1': 1, '2': 2, '3': 3}, 'failed': [], 'rescued': {}, 'entrez_ids': [1, 2, 3],
                          'presents_in_db': {1: True, 2: True, 3: True}})

    def test_to_entrez(self):
        genes = ['SNORD115-43', 'RNA18S5', 'GAGE12F', 'NAT2', 'A1BG', 'SNORD115-48',
                 'Nat2',  # case sensitivity
                 'MDEG']  # other gene
        res = convert_to_entrez('hs', 'symbol', genes)

        self.assertEqual(res.failed[0], 'Nat2')
        self.assertIn('MDEG', res.rescued)
        self.assertIn('Nat2', res.failed)
        self.assertEqual(len(res.converted['SNORD115-48']), 2)

        # All genes are contained in the result
        self.assertItemsEqual(genes, res.converted.keys() + res.failed + res.rescued.keys())

        self.assertEqual(res.get_final_entrez_ids(), [1, 40, 10, 100008588, 10101010101, 100033817, 100008586, 100033822])

    def test_to_symbol(self):
        genes = [1, 10, 100, 1000, 10000, 100008587, 100008586,
                 12345,      # Absents
                 100033819]  # Two symbol genes
        res = convert_entrez_to_symbol('hs', genes)

        self.assertEqual(res['failed'][0], 12345)
        self.assertEqual(len(res['converted'][100033819]), 2)
        self.assertIn('Another', res['converted'][100033819])
        self.assertItemsEqual(res['symbol_ids'],
                              ['RNA5-8S5', 'NAT2', 'AKT3', 'MIR675', 'Another', 'ADA', 'CDH2', 'GAGE12F', 'A1BG'])