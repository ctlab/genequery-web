import os
from constants import ALLOWED_SPECIES, ENTREZ_PATTERN, ENTREZ, REFSEQ, SYMBOL


here = os.path.join


def is_valid_species(species):
    return species in ALLOWED_SPECIES


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