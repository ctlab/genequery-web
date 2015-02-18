import math
import fisher
from scipy.stats import norm
from utils.constants import MM, HS, INF


def calculate_overlaps(modules, query_module):
    query_set = set(query_module)
    overlaps, lengths = {}, {}
    module_ids = []
    for series, platform, module_num, genes in modules:
        if (series, platform) not in overlaps:
            overlaps[series, platform] = {}
            lengths[series, platform] = {}
        overlaps[series, platform][module_num] = len(query_set & genes)
        lengths[series, platform][module_num] = len(genes)
        module_ids.append((series, platform, module_num))
    return module_ids, overlaps, lengths


def fisher_empirical_p_values(species, modules, query_module, max_empirical_p_value=0.01):
    """
    Calculates logarithms of fisher p-value and empirical (adjusted) p-value.

    :param modules: iterable [(series, platform, module_number, set(entrez_ids))]
    :param query_module: [entrez_id]
    :return: [(series, platform, module_number, log(p-value), log(empirical p-value), intersection_size, module_size]
    """
    module_ids, overlaps, lengths = calculate_overlaps(modules, query_module)
    series_overlap = {(s, p): sum(overlaps[s, p].values()) for s, p in overlaps}
    result = []
    for s, p, m in module_ids:
        if overlaps[s, p][m] == 0:
            continue
        p_value = right_p_value(
            overlaps[s, p][m],
            lengths[s, p][m],
            series_overlap[s, p] - overlaps[s, p][m],
            6000 - series_overlap[s, p] - lengths[s, p][m] + overlaps[s, p][m]
        )
        log_p_value = math.log10(p_value) if p_value != 0 else -INF
        empirical_p_val = empirical_p_value(species, log_p_value, len(query_module))
        if empirical_p_val > max_empirical_p_value:
            continue
        log_empirical_p_value = math.log10(empirical_p_val) if empirical_p_val != 0 else -INF
        result.append((s, p, m, log_p_value, log_empirical_p_value, overlaps[s, p][m], lengths[s, p][m]))
    return result


def get_mu(species, module_size):
    if species == MM:
        return -3.06942 - 0.01322 * module_size
    if species == HS:
        return -2.2151 - 0.0187 * module_size
    return None


def get_sigma(species, module_size):
    if species == MM:
        return 0.982519 + 0.000769 * module_size
    if species == HS:
        return 1.027662 + 0.000939 * module_size
    return None


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
        NORM_CACHE[species][module_size] = norm(get_mu(species, module_size), get_sigma(species, module_size))
    return NORM_CACHE[species][module_size]