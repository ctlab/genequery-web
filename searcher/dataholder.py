"""
Import this module on server startup to pre-load required data.
Being loaded once data won't be reloaded until server restart.
"""
import logging
from common.dataset import *
from django.conf import settings
from utils import here, is_dev_mode

LOG = logging.getLogger('genequery')


def create_db_connection():
    import psycopg2
    return psycopg2.connect("dbname={} user={} host='localhost' password={}".format(
        settings.DATABASE_NAME, settings.DATABASE_USER, settings.DATABASE_PASSWORD))


class ModulesDataHolder:
    def get_module(self, species, full_name):
        """
        :type full_name: str
        :type species: str
        :rtype Module or None
        """
        raise NotImplementedError()

    def get_modules(self, species):
        """
        :type species: str
        :rtype list of Module
        """
        raise NotImplementedError()


class ModulesGmtDataHolder(ModulesDataHolder):
    """
    Stores pre-loaded from GMT files modules in memory
    """

    def __init__(self):
        self._datasets = {}
        self._init_species_modules(HS, here(settings.INITIAL_DATA_PATH, 'hs.modules.gmt'))
        self._init_species_modules(MM, here(settings.INITIAL_DATA_PATH, 'mm.modules.gmt'))
        self._init_species_modules(RT, here(settings.INITIAL_DATA_PATH, 'rt.modules.gmt'))

    def _init_species_modules(self, species, path):
        try:
            LOG.info('Initializing modules for {} from {}...'.format(species, path))
            self._datasets[species] = create_dataset_from_gmt(species, path)
        except Exception:
            LOG.exception('Initializing modules failed: {}.'.format(path))

    def get_module(self, species, full_name):
        if species in self._datasets:
            return self._datasets[species].get_module(full_name)
        return None

    def get_modules(self, species):
        if species in self._datasets:
            return self._datasets[species].get_modules()
        return []


class ModulesInMemoryDBDataHolder(ModulesDataHolder):
    """
    Stores pre-loaded from DB modules in memory
    """

    def __init__(self, db_connection):
        self._datasets = {}
        species_to_modules = create_datasets_from_db(db_connection)

        if HS in species_to_modules:
            self._datasets[HS] = species_to_modules[HS]
        if MM in species_to_modules:
            self._datasets[MM] = species_to_modules[MM]
        if RT in species_to_modules:
            self._datasets[RT] = species_to_modules[RT]

    def get_module(self, species, full_name):
        if species in self._datasets:
            return self._datasets[species].get_module(full_name)
        return None

    def get_modules(self, species):
        if species in self._datasets:
            return self._datasets[species].get_modules()
        return []


class ModulesDBDataHolder(ModulesDataHolder):
    """
    Provides access (yeah, it should be DAO...) to modules via DB connection.
    Each call of the methods of this class leads to SQL-query.

    For DEV mode only!
    """

    def __init__(self, db_connection):
        self._conn = db_connection

    def get_module(self, species, full_name):
        cur = self._conn.cursor()
        cur.execute("SELECT species, module, entrez_ids FROM {} WHERE species='{}' and module='{}'"
                    .format(ModulesSqlDAO.table_name, species, full_name))
        m = cur.fetchone()
        return Module(m[0], ModuleName.parse_name(m[1]), m[2])

    def get_modules(self, species):
        cur = self._conn.cursor()
        cur.execute("SELECT species, module, entrez_ids FROM {} WHERE species='{}'"
                    .format(ModulesSqlDAO.table_name, species))
        return [Module(species, ModuleName.parse_name(full_name), entrez_ids)
                for _, full_name, entrez_ids in cur.fetchall()]


def _init_modules_holder(source):
    if is_dev_mode():
        LOG.info('DEV MODE: Using DB to access the modules.')
        return ModulesDBDataHolder(create_db_connection())

    if source == 'db':
        return ModulesInMemoryDBDataHolder(create_db_connection())
    if source == 'files':
        return ModulesGmtDataHolder()
    raise Exception('Unknown modules source: {}.'.format(source))


def _init_id_mapping(source):
    if source == 'db':
        LOG.info('Loading ID mapping from DB')
        return create_id_mapping_from_db(create_db_connection())
    if source == 'files':
        id_mapping_path = here(settings.INITIAL_DATA_PATH, 'id_map.txt')
        LOG.info('Loading ID mapping from {}'.format(id_mapping_path))
        return create_id_mapping_from_file(id_mapping_path)
    raise Exception('Unknown ID mapping source: {}.'.format(source))


def _init_gse_to_title_mapping(source):
    if source == 'db':
        LOG.info('Loading GSE to title mapping from DB')
        return get_gse_to_title_dict_from_db(create_db_connection())
    if source == 'files':
        gse_to_title_path = here(settings.INITIAL_DATA_PATH, 'gse.titles.txt')
        LOG.info('Loading GSE to title mapping from {}'.format(gse_to_title_path))
        return get_gse_to_title_dict_from_file(gse_to_title_path)
    raise Exception('Unknown GSE to title mapping source: {}.'.format(source))


def _init(source):
    """
    :rtype (ModulesDataHolder, IdMapping, dict)
    """
    LOG.info('Initializing data from {}'.format(source))

    modules_data_holder = _init_modules_holder(source)
    id_mapping = _init_id_mapping(source)
    gse_to_title = _init_gse_to_title_mapping(source)

    return modules_data_holder, id_mapping, gse_to_title


init_source_order = getattr(settings, 'INIT_SOURCE_ORDER')

try:
    modules_data_holder, id_mapping, gse_to_title = _init(init_source_order[0])
except Exception, e:
    LOG.exception('Error while initializing data via {}.'.format(init_source_order[0]))
    if len(init_source_order) > 1:
        modules_data_holder, id_mapping, gse_to_title = _init(init_source_order[1])
    else:
        raise Exception('Data is not initialized. Exit.')

print_modules_len = not isinstance(modules_data_holder, ModulesDBDataHolder)
LOG.info(
    'Data has been initialized. hs: {} modules. mm: {} modules. rt: {} modules, ID mapping: {} rows. Titles: {}.'
    .format(
        len(modules_data_holder.get_modules(HS)) if print_modules_len else '--',
        len(modules_data_holder.get_modules(MM)) if print_modules_len else '--',
        len(modules_data_holder.get_modules(RT)) if print_modules_len else '--',
        sum([len(x) for x in id_mapping.rows.values()]),
        len(gse_to_title)
    ))