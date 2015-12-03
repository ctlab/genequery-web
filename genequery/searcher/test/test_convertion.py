from django.test import TestCase
from genequery.searcher.idconvertion import convert_to_entrez, convert_entrez_to_symbol, convert_to_symbol, \
    convert_to_entrez_orthology


class TestIDConvertion(TestCase):
    fixtures = ['symbol_to_entrez.json', 'other_to_entrez.json', 'refseq_to_entrez.json']

    def test_entrez(self):
        convertation = convert_to_entrez('hs', 'entrez', ['1', '2'])
        self.assertItemsEqual({'1': 1, '2': 2}, convertation.converted)
        self.assertItemsEqual([], convertation.failed)
        self.assertItemsEqual([2, 1], convertation.get_final_entrez_ids())

    def test_symbol_to_entrez(self):
        genes = ['SNORD115-43', 'RNA18S5', 'GAGE12F', 'NAT2', 'A1BG', 'SNORD115-48',
                 'Nat2',  # case sensitivity
                 'RESCUED']  # other gene
        res = convert_to_entrez('hs', 'symbol', genes)

        self.assertEqual(res.failed[0], 'Nat2')
        self.assertIn('RESCUED', res.rescued)
        self.assertIn('Nat2', res.failed)
        self.assertEqual(len(res.converted['SNORD115-48']), 2)

        # All genes are contained in the result
        self.assertItemsEqual(genes, res.converted.keys() + res.failed + res.rescued.keys())

        self.assertEqual(res.get_final_entrez_ids(),
                         [1, 40, 10, 100008588, 10101010101, 100033817, 100008586, 100033822])

    def test_refseq_to_entrez(self):
        genes = ['NM_130786', 'NM_000015', 'XM_011544358', 'XM_00000']

        res = convert_to_entrez('hs', 'refseq', genes)

        self.assertEqual('XM_00000', res.failed[0])
        self.assertEqual({}, res.rescued)
        self.assertEqual([1, 10], res.get_final_entrez_ids())

    def test_entrez_to_symbol(self):
        genes = [1, 10, 100, 1000, 10000, 100008587, 100008586,
                 12345,  # Absents
                 100033819]  # Two symbol genes
        res = convert_entrez_to_symbol('hs', genes)

        self.assertEqual(res.failed[0], 12345)
        self.assertEqual(len(res.converted[100033819]), 2)
        self.assertIn('Another', res.converted[100033819])
        self.assertItemsEqual(['RNA5-8S5', 'NAT2', 'NAT222', 'AKT3', 'MIR675', 'Another', 'ADA', 'CDH2', 'GAGE12F', 'A1BG'],
                              res.get_final_symbol_ids())

    def test_symbol_to_symbol(self):
        genes = ['A', 'b']
        res = convert_to_symbol('hs', 'symbol', genes)
        self.assertItemsEqual(genes, res.get_final_symbol_ids())
        self.assertEqual([], res.failed)
        self.assertEqual(['A'], res.converted['A'])

    def test_refseq_to_symbol(self):
        # A1BG; NAT2, NAT222; NAT2, NAT222; AKT3; -
        genes = ['NM_130786', 'NM_000015', 'XM_011544358', 'XM_006724959', 'XM_00000']
        res = convert_to_symbol('hs', 'refseq', genes)

        self.assertItemsEqual(['XM_00000'], res.failed)
        self.assertItemsEqual(['A1BG', 'NAT2', 'NAT222', 'AKT3'], res.get_final_symbol_ids())
        self.assertItemsEqual(['NAT2', 'NAT222'], res.converted['XM_011544358'])
        self.assertItemsEqual(['NAT2', 'NAT222'], res.converted['NM_000015'])

    def test_entrez_to_symbol_common_method(self):
        genes = [1, 10, 100, 1000, 10000, 100008587, 100008586,
                 12345,  # Absents
                 100033819]  # Two symbol genes
        res = convert_to_symbol('hs', 'entrez', genes)

        self.assertEqual(res.failed[0], 12345)
        self.assertEqual(len(res.converted[100033819]), 2)
        self.assertIn('Another', res.converted[100033819])
        self.assertItemsEqual(['RNA5-8S5', 'NAT2', 'NAT222', 'AKT3', 'MIR675', 'Another', 'ADA', 'CDH2', 'GAGE12F', 'A1BG'],
                              res.get_final_symbol_ids())

        res_equal = convert_entrez_to_symbol('hs', genes)
        self.assertItemsEqual(res.converted, res_equal.converted)
        self.assertItemsEqual(res.failed, res_equal.failed)

    def test_make_orthology_refseq(self):
        # 1; 2; 3, 4; 123, --, rescued
        genes = ['XM_005272997', 'XM_006711726', 'XM_006724959', 'XM_00672491111', 'XM_00000']
        res = convert_to_entrez_orthology('mm', 'hs', 'refseq', genes)

        self.assertItemsEqual({'XM_006711726': ['Abcd3', 'Abcd2'],
                               'XM_006724959': ['Abcd3', 'Abcd5', 'Abcd4', 'Abcd6'],
                               'XM_005272997': ['Abcd1'],
                               'XM_00672491111': ['Abcd000']},
                              res.converted_to_symbol)
        self.assertItemsEqual({'XM_006711726': [11, 9], 'XM_006724959': [12, 13, 14], 'XM_005272997': [11]},
                              res.converted_to_entrez)
        self.assertItemsEqual(['XM_00000', 'XM_00672491111'], res.failed)

    def test_make_orthology_entrez(self):
        genes = [1, 2, 3, 4, 123]
        res = convert_to_entrez_orthology('mm', 'hs', 'entrez', genes)

        self.assertItemsEqual(['Abcd000'], res.converted_to_symbol[123])
        self.assertItemsEqual(['Abcd3', 'Abcd4', 'Abcd5'], res.converted_to_symbol[3])
        self.assertItemsEqual([11, 9], res.converted_to_entrez[2])
        self.assertItemsEqual([12, 13], res.converted_to_entrez[3])

    def test_make_orthology_symbol(self):
        genes = ['Abcd1', 'Abcd2', 'Abcd3', 'Abcd000', 'Rescued']
        res = convert_to_entrez_orthology('mm', 'hs', 'symbol', genes)

        self.assertFalse('Abcd000' in res.converted_to_entrez)
        self.assertTrue('Rescued' in res.converted_to_entrez)
        self.assertItemsEqual([9, 11], res.converted_to_entrez['Abcd2'])