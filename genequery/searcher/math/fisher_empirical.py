import math
import fisher
from django.conf import settings
from scipy.stats import norm
from genequery.utils.constants import MM, HS, RT, INF, MIN_LOG_EMPIRICAL_P_VALUE, GENEQUERY_2015_DB_NAME, \
    GENEQUERY_2013_DB_NAME
from genequery.searcher.models import GQModule


BOOTSTRAP_MEAN = {
    GENEQUERY_2013_DB_NAME: {
        HS: lambda x: -0.08455403386 * math.log(x) - 4.269244644,
        MM: lambda x: -0.0869592962 * math.log(x) - 4.090598767,
    },
    GENEQUERY_2015_DB_NAME: {
        HS: lambda x: -0.08347915069 * math.log(x) - 4.443941868,
        MM: lambda x: -0.08848028394 * math.log(x) - 4.269100238,
        RT: lambda x: -0.08350190746 * math.log(x) - 3.568849077,
    }
}

BOOTSTRAP_STD = {
    GENEQUERY_2013_DB_NAME: {
        HS: lambda x: 1.128394343e-6 * x + 0.5539313336,
        MM: lambda x: 2.505819324e-6 * x + 0.5472805136,
    },
    GENEQUERY_2015_DB_NAME: {
        HS: lambda x: -4.909174514e-6 * x + 0.5612293253,
        MM: lambda x: 9.370360256e-6 * x + 0.5418300854,
        RT: lambda x: -1.667001492e-5 * x + 0.5512707705,
    }
}


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
    # noinspection PyCallingNonCallable
    return BOOTSTRAP_MEAN[settings.DATABASE_NAME][species](module_size)


def _get_sigma(species, module_size):
    # noinspection PyCallingNonCallable
    return BOOTSTRAP_STD[settings.DATABASE_NAME][species](module_size)


def get_log10_or_inf(x):
    return math.log10(x) if x != 0 else -INF


def right_p_value(a, b, c, d):
    p_val = fisher.pvalue(a, b, c, d)
    return p_val.right_tail


def empirical_p_value(species, log_p_value, module_size):
    if log_p_value == -INF:
        return 0
    # noinspection PyUnresolvedReferences
    return float(normal_distribution(species, module_size).cdf(log_p_value))


NORM_CACHE = {MM: {}, HS: {}, RT: {}}


def normal_distribution(species, module_size):
    if module_size not in NORM_CACHE[species]:
        NORM_CACHE[species][module_size] = norm(_get_mu(species, module_size), _get_sigma(species, module_size))
    return NORM_CACHE[species][module_size]