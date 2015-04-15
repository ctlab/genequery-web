import os
from django.conf import settings
from constants import SPECIES, ENTREZ_PATTERN, ENTREZ, REFSEQ, SYMBOL


here = os.path.join


def is_valid_species(species):
    return species in SPECIES


def get_module_heat_map_url(series, platform, module_number):
    path_to_image = here('modules', '{}_{}_module_{}.svg'.format(series, platform, module_number))
    path = here(settings.MEDIA_ROOT, path_to_image)
    return here(settings.MEDIA_URL, path_to_image) if os.path.exists(path) else None


def get_gmt_url(species, series, platform):
    path_to_file = here('gmt', species, '{}_{}.gmt'.format(series, platform))
    path = here(settings.MEDIA_ROOT, path_to_file)
    return here(settings.MEDIA_URL, path_to_file) if os.path.exists(path) else None


def parse_module_id(db_module_key):
    """
    Returns [(series, platform, module)] parsed from db module key.
    """
    # TODO make assertions, regexp
    series_platform, module = db_module_key.split('#')
    series, platform = series_platform.split('_')
    return series, platform, module


def get_overlap_length(list1, list2):
    """
    Calculates overlap length (count of common elements) of two sorted in descending order lists.
    :param list1: sorted in descending order list
    :type list1: list
    :param list2: sorted in descending list
    :type list2: list
    :return: overlap length of two sorted in descending order lists
    """
    i, j = 0, 0
    ans = 0
    while i < len(list1) and j < len(list2):
        if list1[i] == list2[j]:
            ans += 1
            i += 1
            j += 1
        elif list1[i] > list2[j]:
            i += 1
        else:
            j += 1
    return ans


def log_get(_log):
    def _logger(a_view):
        def _wrapped_view(request, *args, **kwargs):
            try:
                return a_view(request, *args, **kwargs)
            except Exception, e:
                _log.exception('Error')
        return _wrapped_view
    return _logger


def get_gene_id_type(gene):
    if ENTREZ_PATTERN.match(gene):
        return ENTREZ
    elif is_refseq(gene):
        return REFSEQ
    return SYMBOL


def is_refseq(gene):
    prefixes = ['BE', 'BF', 'BG', 'JX', 'BB', 'BC', 'BM', 'BN', 'BI', 'BK', 'BU', 'BV', 'BP', 'BQ', 'BR', 'JF', 'BX', 'BY',
                'BZ', 'GU', 'D', 'GQ', 'L', 'JQ', 'X', 'GH', 'XM_', 'JN', 'A', 'HQ', 'HM', 'HF', 'HE', 'EL', 'C', 'EI',
                'EH', 'G', 'AM', 'K', 'EF', 'S', 'EX', 'W', 'EU', 'XR_', 'U', 'FR', 'Y', 'FJ', 'FM', 'FN', 'CK', 'CJ',
                'CO', 'CN', 'CL', 'CB', 'CA', 'J', 'CG', 'CF', 'CD', 'R', 'V', 'CR', 'Z', 'CV', 'CT', 'KC', 'KF', 'NM_',
                'DN', 'DY', 'DV', 'DT', 'DR', 'DQ', 'AA', 'AB', 'E', 'AF', 'AI', 'AK', 'AJ', 'M', 'AL', 'AU', 'AW', 'AV',
                'AY', 'AX', 'N', 'CX', 'NR_']
    for p in prefixes:
        g = gene
        if not g.startswith(p):
            continue
        if p not in ['NM_', 'NR_']:
            if '.' not in g:
                continue
            g = g.replace('.', '')
        g = g.replace(p, '')
        if g.isdigit():
            return True
    return False


def gene_list_pprint(genes):
    return '[{}]'.format(' '.join(map(str, genes)))


class GeneQueryException(Exception):
    pass