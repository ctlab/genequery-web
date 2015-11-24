"""
Import this module on server startup to pre-load required data.
Being loaded once data won't be reloaded until server restart.
"""
import logging

from common.dataset import *
from django.conf import settings

from utils import here

LOG = logging.getLogger('genequery')


def get_db_connection():
    import psycopg2
    return psycopg2.connect("dbname={} user={} host='localhost' password={}".format(
        settings.DATABASE_NAME, settings.DATABASE_USER, settings.DATABASE_PASSWORD))


def init_from_files():
    LOG.info('Initializing data from files')
    hs_path = here(settings.INITIAL_DATA_PATH, 'hs.modules.gmt')
    mm_path = here(settings.INITIAL_DATA_PATH, 'mm.modules.gmt')
    id_map_path = here(settings.INITIAL_DATA_PATH, 'id_map.txt')
    gse_titles_path = here(settings.INITIAL_DATA_PATH, 'gse.titles.txt')

    LOG.info('Initializing modules. human: {}, mouse: {}...'.format(hs_path, mm_path))
    datasets = {
        HS: create_dataset_from_gmt(HS, hs_path),
        MM: create_dataset_from_gmt(MM, mm_path)
    }

    LOG.info('Initializing ID mapping from: {}...'.format(id_map_path))
    id_mapping = create_id_mapping_from_file(id_map_path)

    LOG.info('Initializing GSE titles from: {}...'.format(gse_titles_path))
    gse_to_title = get_gse_to_title_dict_from_file(gse_titles_path)

    return datasets, id_mapping, gse_to_title


def init_from_db():
    db_connection = get_db_connection()

    LOG.info('Initializing modules from DB...')
    species_to_modules = create_datasets_from_db(db_connection)

    datasets = {
        HS: DataSet(HS, species_to_modules[HS]),
        MM: DataSet(MM, species_to_modules[MM])
    }

    LOG.info('Initializing ID mapping from DB...')
    id_mapping = create_id_mapping_from_db(db_connection)

    LOG.info('Initializing GSE titles mapping from DB...')
    gse_to_title = get_gse_to_title_dict_from_db(db_connection)

    return datasets, id_mapping, gse_to_title


init_source_order = getattr(settings, 'INIT_SOURCE_ORDER')


# datasets: All modules, {species: list of Module}
# gse_to_title: {gse: title}
try:
    datasets, id_mapping, gse_to_title = (init_from_db if init_source_order[0] == 'db' else init_from_files)()
except Exception, e:
    LOG.exception('Error while initializing data from files.')
    datasets, id_mapping, gse_to_title = (init_from_db if init_source_order[1] == 'db' else init_from_files)()


LOG.info('Data has been initialized. Human: {} modules. Mouse: {} modules. ID mapping: {} rows. Titles: {}.'.format(
    len(datasets[HS]), len(datasets[MM]), sum([len(x) for x in id_mapping.rows.values()]), len(gse_to_title)
))