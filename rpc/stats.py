from SimpleXMLRPCServer import SimpleXMLRPCServer
import SocketServer
import logging
import logging.config
from time import time

from django.conf import settings
from algo.fisher_empirical import fisher_empirical_p_values

from datasources.modulegenes import ModuleGenesDataSource
from utils import is_valid_species


logging.config.dictConfig(settings.LOGGING)
log = logging.getLogger('rpc')


class RPCThreadingServer(SocketServer.ThreadingMixIn, SimpleXMLRPCServer):
    pass


def _error(message):
    return {'result': 'error', 'message': message}


def _ok(data):
    return {'result': 'ok', 'data': data}


class ModuleGenesAccessFunctions:
    data_source = None

    def __init__(self):
        use_raw_db = getattr(settings, 'RPC_USE_RAW_DB_CONNECTION', True)
        log.info("Loading modules [use_raw_db_connection: {}]...".format(use_raw_db))
        t = time()
        self.data_source = ModuleGenesDataSource(raw_db_connection=use_raw_db)
        log.info("{} modules are loaded in {} sec.".format(self.data_source.total_modules(), round(time() - t, 3)))

    def calculate_fisher_empirical_p_values(self, species, entrez_ids, max_empirical_p_value=0.01):
        log.info('Get data {}, {}'.format(species, entrez_ids))
        try:
            if not is_valid_species(species):
                message = "Unknown species: {}".format(species)
                log.warning(message)
                return _error(message)
            start_time = time()
            result = fisher_empirical_p_values(species, self.data_source.items(species), set(entrez_ids),
                                               max_empirical_p_value=max_empirical_p_value)
            log.info('Processing time: {}'.format(time() - start_time))
            return _ok(result)
        except Exception, e:
            log.exception("Error while calculating p-values")
            _error(str(e))


log.info('Starting RPC server at {}...'.format(settings.RPC_ADDRESS))
rpc_server = RPCThreadingServer(settings.RPC_ADDRESS)
rpc_server.register_instance(ModuleGenesAccessFunctions())
try:
    rpc_server.serve_forever()
except KeyboardInterrupt:
    log.info('\nStopping...')
    exit(0)