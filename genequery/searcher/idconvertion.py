import logging
from genequery.searcher.models import Symbol2Entrez, Ensembl2Entrez, Refseq2Entrez, Other2Entrez
from genequery.utils.constants import ENTREZ, REFSEQ, SYMBOL, ENSEMBL, HS
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
    def __init__(self, converted, rescued, failed):
        """
        :type failed: list[str]
        :type rescued: dict[str, list[int]] | dict[int, list[int]]
        :type converted: dict[str, list[int]] | dict[int, list[int]]
        """
        self.converted = converted
        self.rescued = rescued
        self.failed = failed

    def get_final_entrez_ids(self):
        """
        :rtype: list of int
        """
        final_entrez_ids = []
        for genes in self.converted.values():
            final_entrez_ids += genes
        for genes in self.rescued.values():
            final_entrez_ids += genes
        return list(set(final_entrez_ids))

    def get_entrez_ids(self, gene):
        """
        Get entrez ids from either converted or rescued conversion.

        :type gene: str | int
        :rtype: list[int] | None
        """
        if gene in self.converted:
            return self.converted[gene]
        if gene in self.rescued:
            return self.rescued[gene]
        return None

    def get_annotated(self):
        return dict(self.converted.items() + self.rescued.items())


class EntrezToSymbolConversion:
    def __init__(self, converted, failed):
        """
        :type converted: dict[int, list[str]]
        :type failed: list[int]
        """
        self.converted = converted
        self.failed = failed

    def get_final_symbol_ids(self):
        """
        :rtype: list[str]
        """
        result = []
        for v in self.converted.values():
            result += v
        return list(set(result))


class ToSymbolConversion:
    def __init__(self, converted, failed):
        """
        :type converted: dict[int, list[str]] | dict[str, list[str]]
        :type failed: list[str] | list[int]
        """
        self.converted = converted
        self.failed = failed

    def get_final_symbol_ids(self):
        """
        :rtype: list[str]
        """
        result = []
        for v in self.converted.values():
            result += v
        return list(set(result))


class ToEntrezOrthologyConversion:
    def __init__(self, converted_to_symbol, converted_to_entrez, failed):
        """
        :type converted_to_entrez: dict[str, list[int]] | dict[int, list[int]]
        :type failed: list[str] | list[int]
        :type converted_to_symbol: dict[int, list[str]] | dict[str, list[str]]
        :param converted_to_symbol: converted to symbol for query species
        :param converted_to_entrez: converted to entrez for db species
        :param failed: not converted to entrez for db species
        """
        self.converted_to_symbol = converted_to_symbol
        self.failed = failed
        self.converted_to_entrez = converted_to_entrez

    def get_final_entrez_ids(self):
        """
        :rtype: list[int]
        """
        result = []
        for v in self.converted_to_entrez.values():
            result += v
        return list(set(result))


def convert_to_entrez_orthology(query_species, db_species, original_notation, genes):
    """
    :type db_species: str
    :type query_species: str
    :type original_notation: str
    :type genes: list[str] | list[int]
    """
    to_query_symbol = convert_to_symbol(query_species, original_notation, genes)
    adjusted_symbol_ids = adjust_symbol_genes(db_species, to_query_symbol.get_final_symbol_ids())
    to_db_entrez_conversion = convert_to_entrez(db_species, SYMBOL, adjusted_symbol_ids.values())

    failed = {g: True for g in genes}
    to_db_entrez = {}
    for g, symbol_ids in to_query_symbol.converted.items():
        for s in symbol_ids:
            adjusted_s = adjusted_symbol_ids[s]
            entrez_ids = to_db_entrez_conversion.get_entrez_ids(adjusted_s)
            if entrez_ids is not None:
                failed[g] = False
                if g not in to_db_entrez:
                    to_db_entrez[g] = []
                to_db_entrez[g] += entrez_ids
    return ToEntrezOrthologyConversion(converted_to_symbol=to_query_symbol.converted,
                                       converted_to_entrez=to_db_entrez,
                                       failed=[k for k, v in failed.items() if v])


def convert_to_entrez(species, original_notation, genes):
    """
    Converts to entrez (case sensitive).

    :type species: str
    :type original_notation: str
    :type genes: list[str]
    :rtype: ToEntrezConversion
    """
    if original_notation == ENTREZ:
        return ToEntrezConversion({g: [int(g)] for g in genes}, {}, [])

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

    return ToEntrezConversion(converted, rescued, list(not_converted - set(rescued.keys())))


# TODO get rid of this method
def convert_entrez_to_symbol(species, entrez_ids):
    """
    :type species: str
    :type entrez_ids: list[int]
    :rtype: EntrezToSymbolConversion
    """
    # TODO skip query if entrez_ids is empty
    converted_pairs = Symbol2Entrez.objects \
        .filter(entrez_id__in=entrez_ids) \
        .filter(species=species) \
        .values_list('entrez_id', 'symbol_id')

    converted = {}
    for e, s in converted_pairs:
        if e not in converted:
            converted[e] = []
        converted[e].append(s)
    return EntrezToSymbolConversion(converted,
                                    list(set(entrez_ids) - set([p[0] for p in converted_pairs])))


def convert_to_symbol(species, genes_type, genes):
    """
    :type species: str
    :type genes_type: str
    :type genes: list[str] | list[int]
    :rtype: ToSymbolConversion
    """
    if genes_type == SYMBOL:
        return ToSymbolConversion(
            converted={g: [g] for g in genes},
            failed=[],
        )

    if genes_type == ENTREZ:
        to_symbol = convert_entrez_to_symbol(species, genes)
        return ToSymbolConversion(to_symbol.converted, to_symbol.failed)

    to_entrez = convert_to_entrez(species, genes_type, genes)
    to_symbol = convert_entrez_to_symbol(species, to_entrez.get_final_entrez_ids())

    converted = {}
    failed = []
    for g in genes:
        if g in to_entrez.failed or all([e in to_symbol.failed for e in to_entrez.converted[g]]):
            failed.append(g)
            continue

        if g not in converted:
            converted[g] = []

        for e in to_entrez.converted[g]:
            if e in to_symbol.converted:
                converted[g] += to_symbol.converted[e]

    for k in converted:
        converted[k] = list(set(converted[k]))

    return ToSymbolConversion(converted, failed)


def adjust_symbol_genes(for_species, symbol_ids):
    """
    :type for_species: str
    :type symbol_ids: list[str]
    :rtype: dict[str, str]
    """
    if for_species == HS:
        return {gene: gene.upper() for gene in symbol_ids}
    return {gene: gene.capitalize() for gene in symbol_ids}