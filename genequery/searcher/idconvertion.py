import logging

from django.conf import settings

from genequery.searcher.models import Symbol2Entrez, Ensembl2Entrez, Refseq2Entrez, Other2Entrez
from genequery.utils import here
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


class ConversionToEntrezResult:
    def __init__(self, converted, rescued, failed):
        """
        :type failed: list
        :type rescued: dict
        :type converted: dict
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


def convert_to_entrez(species, original_type, genes):
    """
    Converts to entrez (case sensitive).

    :type species: str
    :type original_type: str
    :type genes: list of str
    :rtype: ConversionToEntrezResult
    """
    if original_type == ENTREZ:
        return ConversionToEntrezResult({g: int(g) for g in genes}, {}, [])

    if original_type == SYMBOL:
        model = Symbol2Entrez
        kwargs = {'symbol_id__in': genes}
    elif original_type == ENSEMBL:
        model = Ensembl2Entrez
        kwargs = {'ensembl_id__in': genes}
    elif original_type == REFSEQ:
        model = Refseq2Entrez
        kwargs = {'refseq_id__in': genes}
    else:
        raise Exception('Unknown gene ID type: {}'.format(original_type))

    original_entrez_pairs = list(set(model.objects
                                     .filter(species=species)
                                     .filter(**kwargs)
                                     .values_list('{}_id'.format(original_type), 'entrez_id')))

    not_converted = set(set(genes) - set([pair[0] for pair in original_entrez_pairs]))
    kwargs = {'other_id__in': not_converted}

    rescued_original_entrez_pairs = list(set(Other2Entrez.objects
                                         .filter(species=species)
                                         .filter(**kwargs)
                                         .values_list('other_id', 'entrez_id')))

    converted = {}
    for original, entrez in original_entrez_pairs:
        if original not in converted:
            converted[original] = []
        converted[original].append(entrez)

    rescued = {}
    for other, entrez in rescued_original_entrez_pairs:
        if other not in rescued:
            rescued[other] = []
        rescued[other].append(entrez)

    return ConversionToEntrezResult(converted, rescued, list(not_converted - set(rescued.keys())))


def convert_entrez_to_symbol(species, entrez_ids):
    """
    :type species: str
    :type entrez_ids: list of int
    :rtype: dict
    """
    converted_pairs = Symbol2Entrez.objects\
        .filter(entrez_id__in=entrez_ids)\
        .filter(species=species)\
        .values_list('entrez_id', 'symbol_id')

    converted = {}
    for e, s in converted_pairs:
        if e not in converted:
            converted[e] = []
        converted[e].append(s)

    return {
        'converted': converted,
        'symbol_ids': list(set([p[1] for p in converted_pairs])),
        'failed': list(set(entrez_ids) - set([p[0] for p in converted_pairs]))
    }


ALL_ENTREZ_LISTS_CACHE = {}


def entrez_in_db(species, entrez_ids):
    """
    Returns list of Entrez IDs which aren't contained in DB,
    or empty list if all entrez file isn't available.

    :type entrez_ids: list of int
    :type species: str
    :rtype: (list of int) or None
    """
    if species not in ALL_ENTREZ_LISTS_CACHE:
        try:
            path = here(settings.ALL_ENTREZ_LISTS_PATH, '{}_all_entrez.list'.format(species))
            ALL_ENTREZ_LISTS_CACHE[species] = {[int(e.strip()) for e in open(path).readlines()]}
        except Exception:
            LOG.exception("Can't load all entrez list file for species {}".format(species))
            return []
    return list(set(entrez_ids) - ALL_ENTREZ_LISTS_CACHE[species])