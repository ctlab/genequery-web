import os
from constants import ALLOWED_SPECIES


here = os.path.join


def log_get(_log):
    def _logger(a_view):
        def _wrapped_view(request, *args, **kwargs):
            try:
                return a_view(request, *args, **kwargs)
            except Exception, e:
                _log.exception('Error')
        return _wrapped_view
    return _logger


def gene_list_pprint(genes):
    return '[{}]'.format(' '.join(map(str, genes)))


def only_digits(s):
    """
    Checks if string s consists of digits only.

    :type s: basestring
    :rtype: bool
    """
    try:
        int(s)
        return True
    except ValueError:
        return False