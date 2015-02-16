import os
from django.conf import settings
from constants import SPECIES, ENTREZ_PATTERN, REFSEQ_PATTERN, ENTREZ, REFSEQ, SYMBOL


here = os.path.join


def is_valid_species(species):
    return species in SPECIES


def get_module_heat_map_url(series, platform):
    path_to_image = 'modules/{}_{}.png'.format(series, platform)
    path = here(settings.MEDIA_ROOT, path_to_image)
    return '{}/{}'.format(settings.MEDIA_URL, path_to_image) if os.path.exists(path) else None


def get_gmt_url(species, series, platform):
    path_to_file = 'gmt/{}/{}_{}.gmt'.format(species, series, platform)
    path = here(settings.MEDIA_ROOT, path_to_file)
    return '{}/{}'.format(settings.MEDIA_URL, path_to_file) if os.path.exists(path) else None


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
    elif REFSEQ_PATTERN.match(gene):
        return REFSEQ
    return SYMBOL


class GeneQueryException(Exception):
    pass