import logging
from genequery.searcher.models import Symbol2Entrez, Ensembl2Entrez, Refseq2Entrez, Other2Entrez, Homologene
from genequery.utils.constants import ENTREZ, REFSEQ, SYMBOL, ENSEMBL
import re

ENTREZ_PATTERN = re.compile('^[0-9\s]*$')

LOG = logging.getLogger('genequery')


def get_gene_id_type(gene):
    """
    :type gene: str
    """
    if ENTREZ_PATTERN.match(gene):
        return ENTREZ
    elif is_refseq(gene):
        return REFSEQ
    elif is_ensembl(gene):
        return ENSEMBL
    return SYMBOL


def is_refseq(gene):
    """
    :type gene: str
    :rtype: bool
    """
    prefixes = ['NM', 'NR', 'XM', 'XR']
    return any([gene.startswith('{}_'.format(prefix)) for prefix in prefixes])


def is_ensembl(gene):
    """
    :type gene: str
    :rtype: bool
    """
    # TODO specify more precise prefixes for species
    return gene.startswith('ENS')


class ToEntrezConversion:
    def __init__(self, to_entrez):
        """
        :type to_entrez: dict[str, list[int]] | dict[int, list[int]]
        """
        self.to_entrez = to_entrez

    def get_final_entrez_ids(self):
        """
        :rtype: list of int
        """
        res = []
        for v in self.to_entrez.values():
            res += v
        return list(set(res))

    @staticmethod
    def convert(species, original_notation, genes):
        """
        Converts to entrez (case sensitive).

        :type species: str
        :type original_notation: str
        :type genes: list[str]
        :rtype: ToEntrezConversion
        """
        if original_notation == ENTREZ:
            return ToEntrezConversion({g: [int(g)] for g in genes})

        if original_notation == SYMBOL:
            model = Symbol2Entrez
            kwargs = {'symbol_id__in': genes}
        elif original_notation == ENSEMBL:
            model = Ensembl2Entrez
            kwargs = {'ensembl_id__in': genes}
        elif original_notation == REFSEQ:
            model = Refseq2Entrez
            kwargs = {'refseq_id__in': genes}
        else:
            raise Exception('Unknown gene ID type: {}'.format(original_notation))

        original_entrez_pairs = list(set(model.objects
                                         .filter(species=species)
                                         .filter(**kwargs)
                                         .values_list('{}_id'.format(original_notation), 'entrez_id')))

        not_converted = set(set(genes) - set([pair[0] for pair in original_entrez_pairs]))

        rescued = {}
        if original_notation == SYMBOL:
            # rescue
            kwargs = {'other_id__in': not_converted}
            rescued_original_entrez_pairs = list(set(Other2Entrez.objects
                                                     .filter(species=species)
                                                     .filter(**kwargs)
                                                     .values_list('other_id', 'entrez_id')))
            for other, entrez in rescued_original_entrez_pairs:
                if other not in rescued:
                    rescued[other] = []
                rescued[other].append(entrez)

        converted = {}
        for original, entrez in original_entrez_pairs:
            if original not in converted:
                converted[original] = []
            converted[original].append(entrez)

        to_entrez = {g: [] for g in genes}
        for g in genes:
            if g in converted:
                to_entrez[g] += converted[g]
            if g in rescued:
                to_entrez[g] += rescued[g]

        return ToEntrezConversion(to_entrez)


class ToSymbolConversion:
    def __init__(self, to_symbol):
        """
        :type to_symbol: dict[int, list[str]] | dict[str, list[str]]
        """
        self.to_symbol = to_symbol

    def get_final_symbol_ids(self):
        """
        :rtype: list[str]
        """
        result = []
        for v in self.to_symbol.values():
            result += v
        return list(set(result))

    @staticmethod
    def _convert_entrez_to_symbol(species, entrez_ids):
        """
        :type species: str
        :type entrez_ids: list[int]
        :rtype: EntrezToSymbolConversion
        """
        if not entrez_ids:
            return ToSymbolConversion({})
        converted_pairs = Symbol2Entrez.objects.filter(entrez_id__in=entrez_ids).filter(species=species)\
            .values_list('entrez_id', 'symbol_id')

        to_symbol = {}
        for e, s in converted_pairs:
            if e not in to_symbol:
                to_symbol[e] = []
            to_symbol[e].append(s)

        for g in entrez_ids:
            if g not in to_symbol:
                to_symbol[g] = []

        return ToSymbolConversion(to_symbol)

    @staticmethod
    def convert(species, genes_type, genes):
        """
        :type species: str
        :type genes_type: str
        :type genes: list[str] | list[int]
        :rtype: ToSymbolConversion
        """
        if genes_type == SYMBOL:
            return ToSymbolConversion(to_symbol={g: [g] for g in genes})

        if genes_type == ENTREZ:
            return ToSymbolConversion._convert_entrez_to_symbol(species, genes)

        to_entrez_conversion = ToEntrezConversion.convert(species, genes_type, genes)
        to_symbol_conversion = ToSymbolConversion._convert_entrez_to_symbol(species,
                                                                            to_entrez_conversion.get_final_entrez_ids())

        to_final_symbol = {g: [] for g in genes}
        for g in genes:
            for eid in to_entrez_conversion.to_entrez[g]:
                to_final_symbol[g] += to_symbol_conversion.to_symbol.get(eid, [])

        return ToSymbolConversion(to_symbol=to_final_symbol)


class ToEntrezOrthologyConversion:
    def __init__(self, to_final_entrez, to_proxy_entrez=None):
        """
        :type to_final_entrez: dict[str, list[int]] | dict[int, list[int]]
        :type to_final_entrez: dict[str, list[int]] | dict[int, list[int]]

        """
        self.to_final_entrez = to_final_entrez
        self.to_proxy_entrez = to_proxy_entrez

    def get_final_entrez_ids(self):
        """
        :rtype: list[int]
        """
        result = []
        for v in self.to_final_entrez.values():
            result += v
        return list(set(result))

    def get_final_entrez_ids_by_gene(self, gene):
        """
        Return final entrez IDs by gene or empty list if there's no entrez for the gene.

        :type gene: str | int
        :rtype list[int]
        """
        genes = [gene]
        if self.to_proxy_entrez is not None:
            return self.to_proxy_entrez.get(gene, [])
        result = []
        for g in genes:
            result += self.to_final_entrez[g]
        return result

    @staticmethod
    def convert(query_species, db_species, original_notation, genes):
        """
        :type db_species: str
        :type query_species: str
        :type original_notation: str
        :type genes: list[str] | list[int]
        """
        if original_notation != ENSEMBL:
            original_field_name = '{}_id'.format(original_notation)
            filter_kwargs = {
                '{}__in'.format(original_field_name): genes,
                'species': query_species,
            }
            original2group = dict(Homologene.objects.filter(**filter_kwargs).values_list(
                original_field_name, 'group_id'))
            group2entrez = dict(Homologene.objects.filter(
                species=db_species, group_id__in=original2group.values()
            ).values_list('group_id', 'entrez_id'))

            to_final_entrez = {g: [] for g in genes}
            for gene in genes:
                final_eid = group2entrez.get(original2group.get(gene))
                if final_eid:
                    to_final_entrez[gene].append(final_eid)

            return ToEntrezOrthologyConversion(to_final_entrez=to_final_entrez)

        to_proxy_entrez_conversion = ToEntrezConversion.convert(query_species, original_notation, genes)
        final_conversion = ToEntrezOrthologyConversion.convert(
            query_species, db_species, 'entrez', to_proxy_entrez_conversion.get_final_entrez_ids()
        )
        to_final_entrez = {}
        to_proxy_entrez = {}
        for g in genes:
            to_proxy_entrez[g] = to_proxy_entrez_conversion.to_entrez[g]
            to_final_entrez[g] = []
            for eid in to_proxy_entrez[g]:
                to_final_entrez[g] += final_conversion.get_final_entrez_ids_by_gene(eid)

        return ToEntrezOrthologyConversion(to_final_entrez=to_final_entrez, to_proxy_entrez=to_proxy_entrez)