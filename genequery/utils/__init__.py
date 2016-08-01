import os

from django.core.exceptions import PermissionDenied
from django.utils.six import wraps


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


def only_digits_with_dot(s):
    """
    Checks if string s consists of digits only (with one not leading dot probably).

    :type s: str
    :rtype: bool
    """
    if not s or s[0] == '.':
        return False
    try:
        float(s)
        return True
    except ValueError:
        return False


def require_ajax(view):
    @wraps(view)
    def _wrapped_view(self_view, request, *args, **kwargs):
        if request.is_ajax():
            return view(self_view, request, *args, **kwargs)
        else:
            raise PermissionDenied()
    return _wrapped_view