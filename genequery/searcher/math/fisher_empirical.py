import math
import fisher
from scipy.stats import norm
from genequery.utils.constants import MM, HS, INF, MIN_LOG_EMPIRICAL_P_VALUE
from genequery.searcher.models import GQModule


class FisherCalculationResult:
    def __init__(self, gse, gpl, module_number, module_size, intersection_size,
                 pvalue=None, empirical_pvalue=None,
                 log10_pvalue=None, log10_emp_pvalue=None):
        """
        :type log10_pvalue: float
        :type log10_emp_pvalue: float
        :type intersection_size: int
        :type empirical_pvalue: float
        :type pvalue: float
        :type gse: str
        :type gpl: str
        :type module_number: int
        :type module_size: int
        """
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

        if empirical_pvalue is None and log10_emp_pvalue is None:
            raise Exception('Both empirical ep-value and log(empirical p-value) are None.')
        if empirical_pvalue is not None:
            self.emp_pvalue = empirical_pvalue
            self.log_emp_pvalue = get_log10_or_inf(empirical_pvalue)
        else:
            self.emp_pvalue = math.pow(10, log10_emp_pvalue)
            self.log_emp_pvalue = log10_emp_pvalue

        if self.log_emp_pvalue < MIN_LOG_EMPIRICAL_P_VALUE:
            self.log_emp_pvalue = -INF

    def __cmp__(self, other):
        if self.log_pvalue == other.log_pvalue:
            return 0
        return 1 if self.log_pvalue > other.log_pvalue else -1

    def __repr__(self):
        return 'FisherResult[module={},inters={},log_pvalue={},log_emp_pvalue={}'.format(
            GQModule.merge_full_name(self.gse, self.gpl, self.module_number),
            self.intersection_size, self.log_emp_pvalue, self.log_emp_pvalue)


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


def fisher_empirical_p_values(species, modules, entrez_query, max_empirical_p_value=0.01):
    """
    Calculates logarithm of fisher p-value and empirical (adjusted) p-value.

    :type modules: iterable of GQModule
    :type max_empirical_p_value: float
    :param max_empirical_p_value: max allowed empirical p-value
    :param species: species
    :type species: str
    :param entrez_query: list of entrez ids
    :type entrez_query: list of int
    :return: [(series, platform, module_number, log(p-value), log(empirical p-value), intersection_size, module_size]
    :rtype: list of FisherCalculationResult
    """
    overlaps_with_each_module = calculate_overlaps(modules, entrez_query)
    overlaps_with_whole_gse = {(s, p): sum(overlaps_with_each_module[s, p].values())
                               for s, p in overlaps_with_each_module}
    result = []
    for module in modules:
        gse, gpl, num = module.split_full_name()
        if overlaps_with_each_module[gse, gpl][num] == 0:
            continue
        pvalue = right_p_value(
            overlaps_with_each_module[gse, gpl][num],
            len(module.entrez_ids) - overlaps_with_each_module[gse, gpl][num],
            overlaps_with_whole_gse[gse, gpl] - overlaps_with_each_module[gse, gpl][num],
            6000 - overlaps_with_whole_gse[gse, gpl] - len(module.entrez_ids) + overlaps_with_each_module[gse, gpl][num]
        )
        log_pvalue = get_log10_or_inf(pvalue)
        empirical_pvalue = empirical_p_value(species, log_pvalue, len(entrez_query))
        if empirical_pvalue > max_empirical_p_value:
            continue
        result.append(
            FisherCalculationResult(gse, gpl, num, len(module.entrez_ids),
                                    overlaps_with_each_module[gse, gpl][num],
                                    pvalue=pvalue,
                                    empirical_pvalue=empirical_pvalue)
        )
    return result


def _get_mu(species, module_size):
    if species == MM:
        return -3.06942 - 0.01322 * module_size
    if species == HS:
        return -2.2151 - 0.0187 * module_size
    return None


def _get_sigma(species, module_size):
    if species == MM:
        return 0.982519 + 0.000769 * module_size
    if species == HS:
        return 1.027662 + 0.000939 * module_size
    return None


def get_log10_or_inf(x):
    return math.log10(x) if x != 0 else -INF


def right_p_value(a, b, c, d):
    p_val = fisher.pvalue(a, b, c, d)
    return p_val.right_tail


def empirical_p_value(species, log_p_value, module_size):
    if log_p_value == -INF:
        return 0
    return float(normal_distribution(species, module_size).cdf(log_p_value))


NORM_CACHE = {MM: {}, HS: {}}


def normal_distribution(species, module_size):
    if module_size not in NORM_CACHE[species]:
        NORM_CACHE[species][module_size] = norm(_get_mu(species, module_size), _get_sigma(species, module_size))
    return NORM_CACHE[species][module_size]