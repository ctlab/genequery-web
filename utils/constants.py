import re

ENTREZ_PATTERN = re.compile('^[0-9\s]*$')
REFSEQ_PATTERN = re.compile('^[0-9\sNMR_]*$')

ENTREZ = 'entrez'
REFSEQ = 'refseq'
SYMBOL = 'symbol'

INF = 1e10
EPS = 1e-325
MIN_LOG_EMPIRICAL_P_VALUE = -325

HS = 'hs'
MM = 'mm'

SPECIES = (HS, MM)