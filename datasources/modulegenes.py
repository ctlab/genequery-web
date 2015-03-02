from django.conf import settings
import gc

from searcher.models import ModuleGenes
from utils import parse_module_id
from utils.constants import MM, HS


def get_db_connection():
    import psycopg2
    return psycopg2.connect("dbname={} user={} host='localhost' password={}".format(
        settings.DATABASE_NAME, settings.DATABASE_USER, settings.DATABASE_PASSWORD))


def _load_data(raw_db_connection=False, species=None):
    if raw_db_connection:
        conn = get_db_connection()
        cur = conn.cursor()
        if species:
            cur.execute("SELECT * FROM {} WHERE species='{}'".format(ModuleGenes._meta.db_table, species))
        else:
            cur.execute("SELECT * FROM {}".format(ModuleGenes._meta.db_table))
        return cur.fetchall()
    import django
    django.setup()
    if species:
        query_prefix = ModuleGenes.objects.filter(species=species)
    else:
        query_prefix = ModuleGenes.objects.all()
    return list(query_prefix.values_list('species', 'module', 'entrez_ids'))


def get_data_items(raw_db_connection=False):
    result = {MM: [], HS: []}
    rows = _load_data(raw_db_connection)
    for sp, module_id, genes in rows:
        series, platform, module_num = parse_module_id(module_id)
        result[sp].append((series, platform, module_num, set(genes)))
    return result


class ModuleGenesDataSource:
    data_items = {HS: [], MM: []}

    def __init__(self, raw_db_connection=False):
        if self.data_items == {HS: [], MM: []}:
            rows = _load_data(raw_db_connection)
            for sp, module_id, genes in rows:
                series, platform, module_num = parse_module_id(module_id)
                self.data_items[sp].append((series, platform, module_num, set(genes)))

    def total_modules(self):
        return len(self.data_items[MM]) + len(self.data_items[HS])

    def items(self, species):
        return self.data_items[species]


class ModuleGenesChunkDataSource:
    chunk = None
    first_not_loaded = 0
    chunk_size = getattr(settings, 'MODULE_GENES_CHUNK_SIZE', 10000)

    def __init__(self, species):
        self._total_modules = ModuleGenes.objects.filter(species=species).count()

    def total_modules(self):
        return self._total_modules

    def items(self, species):
        for i in xrange(self._total_modules):
            if i == self._total_modules:
                self.chunk = None
                gc.collect()
                return
            if i == self.first_not_loaded:
                self.chunk = None
                gc.collect()
                self.first_not_loaded = min(self._total_modules, self.first_not_loaded + self.chunk_size)
                self.chunk = list(ModuleGenes.objects.filter(
                    species=species).order_by('module')[i:self.first_not_loaded].values_list(
                    'species', 'module', 'entrez_ids'))
            sp, module_id, genes = self.chunk[i % self.chunk_size]
            series, platform, module_num = parse_module_id(module_id)
            yield series, platform, module_num, set(genes)