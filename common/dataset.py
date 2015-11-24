from common.constants import *
from common.dao import ModulesGmtDAO, ModulesSqlDAO, IdMappingFileDAO, IdMappingSqlDAO, GseTitlesFileDAO, \
    GseTitlesSqlDAO


class ModuleName:
    def __init__(self, gse, gpl, module_number):
        """
        :type gse: str
        :type gpl: str
        :type module_number: int
        """
        self.gse = gse
        self.gpl = gpl
        self.module_number = module_number

        self.full = '{}_{}#{}'.format(gse, gpl, module_number)

    def __eq__(self, other):
        return self.full == other.full_name

    def __str__(self):
        return self.full

    @staticmethod
    def parse_name(full_name):
        """
        Convert full name string of form GSE_GPL#MODULE_NUMBER to ModuleName object
        :type full_name: string
        :rtype ModuleName
        """
        gse_gpl, module_number = full_name.split('#')
        gse, gpl = gse_gpl.split('_')
        return ModuleName(gse, gpl, int(module_number))

    @staticmethod
    def build_full(gse, gpl, module_number):
        """
        Create full module name like GSE_GPL#module_number
        :type module_number: int
        :type gpl: str
        :type gse: str
        :rtype str
        """
        return ModuleName(gse, gpl, module_number).full


class Module:
    def __init__(self, species, module_name, entrez_ids):
        """
        :type species: str
        :type module_name: ModuleName
        :type entrez_ids: list of int
        """
        self.species = species
        self.name = module_name
        self.gene_ids_set = set(entrez_ids)

    def __str__(self):
        return '{}[species:{},genes:{}]'.format(self.name, self.species, len(self.gene_ids_set))

    def __len__(self):
        return len(self.gene_ids_set)

    def __repr__(self):
        return 'Module<{}>'.format(str(self))


class DataSet:
    def __init__(self, species, modules):
        """
        :type species: str
        :param modules: list of Module
        """
        self.species = species
        self.name_to_module = {m.name.full: m for m in modules}

    def __len__(self):
        return len(self.name_to_module)

    def __str__(self):
        return 'DataSet[species:{},modules:{}]'.format(self.species, len(self.name_to_module))

    def get_module(self, full_name):
        """
        :rtype: Module or None
        :type full_name: str
        """
        return self.name_to_module.get(full_name, None)

    def get_modules(self):
        """
        Get all modules.

        :rtype list of Module
        """
        return self.name_to_module.values()


def create_dataset_from_gmt(species, filepath):
    dict_modules = ModulesGmtDAO(filepath, species).get_modules()
    return DataSet(species, [Module(x['species'], ModuleName.parse_name(x['full_name']), x['entrez_ids'])
                             for x in dict_modules])


def create_datasets_from_db(db_connection):
    """
    :param db_connection: (postgres) data base connection
    :returns {species: list of Module}
    :rtype: dict
    """
    species_to_modules = {}
    dict_modules = ModulesSqlDAO(db_connection).get_modules()
    for m in dict_modules:
        if m['species'] not in species_to_modules:
            species_to_modules[m['species']] = []
        species_to_modules[m['species']].append(
            Module(m['species'], ModuleName.parse_name(m['full_name']), m['entrez_ids'])
        )
    return species_to_modules


class IdTuple:
    def __init__(self, entrez_id=None, symbol_id=None, refseq_id=None):
        """
        :type entrez_id: int
        :type refseq_id: str or None
        :type symbol_id: str or None
        """
        self.entrez_id = entrez_id
        self.symbol_id = symbol_id
        self.refseq_id = refseq_id

    def __str__(self):
        return 'Id[{},{},{}]'.format(self.entrez_id, self.refseq_id, self.symbol_id)

    def __repr__(self):
        return str(self)


NO_GENE = '-'


class IdMapping:
    #  TODO it's more efficient in terms of processing time to store separate map for every notation type
    rows = {}  # {species: [IdTuple]}

    def __init__(self, raw_tuples):
        """
        Create ID mapping from list of raw tuples (species, entrez_id, refseq_id, symbol_id)

        :type raw_tuples: list of (str, str, str, str)
        """
        for species, entrez, refseq, symbol in raw_tuples:
            refseq = refseq if refseq != NO_GENE else None
            symbol = symbol if symbol != NO_GENE else None

            if species not in self.rows:
                self.rows[species] = []

            self.rows[species].append(IdTuple(entrez_id=int(entrez), refseq_id=refseq, symbol_id=symbol))

    def convert_to_entrez(self, species, notation_type, genes):
        """
        Convert genes to entrez notation.
        Returns list of pairs where every pair is tuple of two values:
            entrez ID and original ID for every gene from input genes.

        :type genes: list of (int or str)
        :type notation_type: str
        :type species: str
        :rtype: list of (int, int or str)
        :returns list of pairs: (entrez ID, original gene ID)
        """
        if notation_type == ENTREZ:
            #  No mapping is required
            return list(set([(int(g), g) for g in genes]))

        genes = set(genes)

        if notation_type == SYMBOL:
            return list(set([(row.entrez_id, row.symbol_id) for row in self.rows[species] if row.symbol_id in genes]))

        if notation_type == REFSEQ:
            return list(set([(row.entrez_id, row.refseq_id) for row in self.rows[species] if row.refseq_id in genes]))

        raise Exception('Unknown notation type: {}'.format(notation_type))


def create_id_mapping_from_file(path):
    """
    :type path: str
    :rtype: IdMapping
    """
    return IdMapping(IdMappingFileDAO(path).get_id_mapping_rows())


def create_id_mapping_from_db(db_connection):
    """
    :param db_connection: (postgres) data base connection
    :rtype: IdMapping
    """
    return IdMapping(IdMappingSqlDAO(db_connection).get_id_mapping_rows())


def get_gse_to_title_dict_from_file(path):
    """
    :type path: str
    :rtype: dict
    """
    return dict(GseTitlesFileDAO(path).get_titles())


def get_gse_to_title_dict_from_db(db_connection):
    """
    :param db_connection: (postgres) data base connection
    :rtype: dict
    """
    return dict(GseTitlesSqlDAO(db_connection).get_titles())