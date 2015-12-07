from django.test import TestCase
from genequery.searcher.idconvertion import ToEntrezConversion, ToSymbolConversion, ToEntrezOrthologyConversion


class TestIDConvertion(TestCase):
    fixtures = ['symbol_to_entrez.json', 'other_to_entrez.json', 'refseq_to_entrez.json', 'ensembl_to_entrez.json',
                'homologene.json']

    def test_entrez_to_entrez(self):
        res = ToEntrezConversion.convert('hs', 'entrez', ['1', '2'])
        self.assertItemsEqual({'1': [1], '2': [2]}, res.to_entrez)
        self.assertItemsEqual([2, 1], res.get_final_entrez_ids())

    def test_symbol_to_entrez(self):
        genes = ['SNORD115-43', 'RNA18S5', 'GAGE12F', 'NAT2', 'A1BG', 'SNORD115-48',
                 'Nat2',  # case sensitivity
                 'RESCUED']  # other gene
        res = ToEntrezConversion.convert('hs', 'symbol', genes)

        self.assertEqual([], res.to_entrez['Nat2'])
        self.assertEqual([40], res.to_entrez['RESCUED'])
        self.assertEqual([], res.to_entrez['Nat2'])
        self.assertEqual(len(res.to_entrez['SNORD115-48']), 2)

        self.assertItemsEqual(genes, res.to_entrez.keys())

        self.assertEqual(res.get_final_entrez_ids(),
                         [1, 40, 10, 100008588, 10101010101, 100033817, 100008586, 100033822])

    def test_refseq_to_entrez(self):
        genes = ['NM_130786', 'NM_000015', 'XM_011544358', 'XM_00000']

        res = ToEntrezConversion.convert('hs', 'refseq', genes)

        self.assertEqual([], res.to_entrez['XM_00000'])
        self.assertEqual([1, 10], res.get_final_entrez_ids())

    def test_entrez_to_symbol(self):
        genes = [1, 10, 100, 1000, 10000, 100008587, 100008586,
                 12345,  # Absents
                 100033819]  # Two symbol genes
        res = ToSymbolConversion.convert('hs', 'entrez', genes)

        self.assertEqual([], res.to_symbol[12345])
        self.assertEqual(2, len(res.to_symbol[100033819]))
        self.assertEqual(['Another', 'MIR675'], res.to_symbol[100033819])
        self.assertItemsEqual(['RNA5-8S5', 'NAT2', 'NAT222', 'AKT3', 'MIR675', 'Another', 'ADA', 'CDH2', 'GAGE12F', 'A1BG'],
                              res.get_final_symbol_ids())

    def test_symbol_to_symbol(self):
        genes = ['A', 'b']
        res = ToSymbolConversion.convert('hs', 'symbol', genes)
        self.assertItemsEqual(genes, res.get_final_symbol_ids())
        self.assertEqual(['A'], res.to_symbol['A'])

    def test_refseq_to_symbol(self):
        # A1BG; NAT2, NAT222; NAT2, NAT222; AKT3; -
        genes = ['NM_130786', 'NM_000015', 'XM_011544358', 'XM_006724959', 'XM_00000']
        res = ToSymbolConversion.convert('hs', 'refseq', genes)

        self.assertEqual([], res.to_symbol['XM_00000'])
        self.assertItemsEqual(['A1BG', 'NAT2', 'NAT222', 'AKT3'], res.get_final_symbol_ids())
        self.assertItemsEqual(['NAT2', 'NAT222'], res.to_symbol['XM_011544358'])
        self.assertItemsEqual(['NAT2', 'NAT222'], res.to_symbol['NM_000015'])

    def test_homologene_symbol(self):
        genes = ['ACADM', 'ACADVL', 'AGT', 'NOSYMBOL']
        res = ToEntrezOrthologyConversion.convert('hs', 'mm', 'symbol', genes)

        self.assertEqual([11606], res.to_final_entrez['AGT'])
        self.assertEqual(None, res.to_proxy_entrez)
        self.assertEqual([], res.to_final_entrez['NOSYMBOL'])

    def test_homologene_entrez(self):
        genes = [11364, 11370, 1234567]
        res = ToEntrezOrthologyConversion.convert('mm', 'rt', 'entrez', genes)

        self.assertEqual([24158], res.to_final_entrez[11364])
        self.assertEqual(None, res.to_proxy_entrez)
        self.assertEqual([], res.to_final_entrez[1234567])

    def test_homologene_ensembl(self):
        # one entrez | two entrez | no entrez | no final entrez
        genes = ['ENSG00000114771', 'ENSG00000165029', 'ENSG0000000000', 'ENSG123456']
        res = ToEntrezOrthologyConversion.convert('hs', 'mm', 'ensembl', genes)

        self.assertEqual([], res.to_final_entrez['ENSG0000000000'])

        self.assertEqual([], res.to_final_entrez['ENSG123456'])
        self.assertEqual([101010], res.to_proxy_entrez['ENSG123456'])

        self.assertEqual([11370, 11364], res.to_final_entrez['ENSG00000165029'])
        self.assertEqual([37, 34], res.to_proxy_entrez['ENSG00000165029'])

        self.assertEqual([11477], res.to_final_entrez['ENSG00000114771'])