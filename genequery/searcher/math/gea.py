import math
import fisher
from genequery.utils.constants import INF, BONFERRONI_THRESHOLD
from genequery.searcher.models import GQModule


class EnrichmentResultItem:
    def __init__(self, gse, gpl, module_number, module_size, intersection_size, species,
                 pvalue=None, log10_pvalue=None):
        """
        :type log10_pvalue: float
        :type intersection_size: int
        :type pvalue: float
        :type gse: str
        :type gpl: str
        :type module_number: int
        :type module_size: int
        :type species: str
        """
        self.species = species
        self.gse = gse
        self.gpl = gpl
        self.module_number = module_number
        self.module_size = module_size
        self.intersection_size = intersection_size

        if pvalue is None and log10_pvalue is None:
            raise Exception('Both p-value and log(p-value) are None.')
        if pvalue is not None:
            self.pvalue = pvalue
            self.log_pvalue = get_log10_or_inf(pvalue)
        else:
            self.pvalue = math.pow(10, log10_pvalue)
            self.log_pvalue = log10_pvalue

        self.adj_p_value = bonferroni_correction_of_inf(self.pvalue, species=species)
        self.log_adj_p_value = get_log10_or_inf(self.adj_p_value)

    def __cmp__(self, other):
        if self.log_pvalue == other.log_pvalue:
            return 0
        return 1 if self.log_pvalue > other.log_pvalue else -1

    def __repr__(self):
        return 'EnrichmentResultItem[module={},inters={},lg(adj-p-value)={}'.format(
            GQModule.merge_full_name(self.gse, self.gpl, self.module_number),
            self.intersection_size, self.log_adj_p_value)


def calculate_overlaps(modules, query):
    """
    Calculates overlaps of query genes with each module from modules.

    :param query: sorted list of entrez IDs
    :type query: list of int
    :type modules: list of GQModule
    :returns dictionary of the form {(gse, gpl): {module_number: overlap length, ...}, ...}
    :rtype dict
    """
    query_set = set(query)
    overlaps = {}
    for module in modules:
        gse, gpl, module_number = module.split_full_name()
        module_genes = module.entrez_ids
        if (gse, gpl) not in overlaps:
            overlaps[gse, gpl] = {}
        overlaps[gse, gpl][module_number] = len(query_set & set(module_genes))
    return overlaps


def calculate_gse_sizes(modules):
    """
    Calculate size of GSEs whose modules are presented in `modules` argument.

    :type modules: iterable of GQModule
    :rtype: dict[(str,str), int]
    """
    sizes = {}
    for module in modules:
        gse, gpl, module_number = module.split_full_name()
        if (gse, gpl) not in sizes:
            sizes[(gse, gpl)] = 0
        sizes[(gse, gpl)] += len(module.entrez_ids)
    return sizes


def calculate_fisher_p_values(species, modules, entrez_query, max_lg_p_value=None):
    """
    Calculates logarithm of fisher p-value and empirical (adjusted) p-value.
    Bonferroni correction is used by default.

    :type modules: iterable of GQModule
    :type max_lg_p_value: float
    :param max_lg_p_value: max allowed empirical p-value
    :param species: species
    :type species: str
    :param entrez_query: list of entrez ids
    :type entrez_query: list of int
    :return: [(series, platform, module_number, log(p-value), log(empirical p-value), intersection_size, module_size]
    :rtype: list of EnrichmentResultItem
    """
    max_lg_p_value = max_lg_p_value if max_lg_p_value is not None else BONFERRONI_THRESHOLD[species]
    overlaps_with_each_module = calculate_overlaps(modules, entrez_query)
    sizes = calculate_gse_sizes(modules)
    overlaps_with_whole_gse = {(s, p): sum(overlaps_with_each_module[s, p].values())
                               for s, p in overlaps_with_each_module}
    result = []
    for module in modules:
        gse, gpl, num = module.split_full_name()
        if overlaps_with_each_module[gse, gpl][num] == 0:
            continue
        a = overlaps_with_each_module[gse, gpl][num]
        b = len(module.entrez_ids) - a
        c = overlaps_with_whole_gse[gse, gpl] - a
        d = sizes[gse, gpl] - overlaps_with_whole_gse[gse, gpl] - b
        pvalue = right_p_value(a, b, c, d)
        lg_pvalue = get_log10_or_inf(pvalue)
        if lg_pvalue > max_lg_p_value:
            continue
        result.append(
            EnrichmentResultItem(gse, gpl, num, len(module.entrez_ids),
                                 overlaps_with_each_module[gse, gpl][num], species,
                                 pvalue=pvalue, log10_pvalue=lg_pvalue))
    return result


def right_p_value(a, b, c, d):
    p_val = fisher.pvalue(a, b, c, d)
    return p_val.right_tail


def get_log10_or_inf(x):
    return math.log10(x) if x != 0 else -INF


def log10_bonferroni_correction_of_inf(log_p_value, species):
    """
    Return log_p_value after Bonferroni correction on modules count for the species.

    :type species: str
    :type log_p_value: float
    """
    from django.conf import settings
    return (log_p_value - settings.BONFERRONI_ADJ_LOG_P_VALUE[species]) if log_p_value != -INF else -INF


def bonferroni_correction_of_inf(p_value, species):
    """
    Return p_value after Bonferroni correction on modules count for the species.

    :type species: str
    :type p_value: float
    """
    from django.conf import settings
    return p_value * settings.MODULES_COUNT[species]