class ModulesDAO:
    def get_modules(self):
        """
        :returns: {species: str, full_name: str, entrez_ids: list of int}
        :rtype list of dict
        """
        raise NotImplementedError()


class ModulesSqlDAO(ModulesDAO):
    table_name = 'module_genes'

    def __init__(self, db_connection):
        self.conn = db_connection

    def get_modules(self):
        cur = self.conn.cursor()
        cur.execute("SELECT species, module, entrez_ids FROM {}".format(self.table_name))
        return [{'species': species, 'full_name': full_name, 'entrez_ids': entrez_ids}
                for species, full_name, entrez_ids in cur.fetchall()]


class ModulesGmtDAO(ModulesDAO):
    def __init__(self, path, species):
        """
        :type path: str
        :type species: str
        """
        self.gmt_lines = [line.strip() for line in open(path).readlines()]
        self.species = species

    def get_modules(self):
        modules = []
        for line in self.gmt_lines:
            full_name, comma_separated_genes = line.split('\t')
            gene_ids = map(int, comma_separated_genes.split(','))
            modules.append({'species': self.species, 'full_name': full_name, 'entrez_ids': gene_ids})
        return modules


class IdMappingDAO:
    def get_id_mapping_rows(self):
        """
        :returns list of (species, entrez, refseq, symbol)
        :rtype: list of (str, str, str, str)
        """
        raise NotImplementedError()


class IdMappingFileDAO(IdMappingDAO):
    def __init__(self, path):
        """
        :type path: str
        """
        self.path = path

    def get_id_mapping_rows(self):
        raw_tuples = []

        for line in [line.strip() for line in open(self.path).readlines()]:
            species, entrez_id, refseq_id, symbol_id = line.split('\t')
            raw_tuples.append((species, entrez_id, refseq_id, symbol_id))

        return raw_tuples


class IdMappingSqlDAO(IdMappingDAO):
    table_name = 'id_map'

    def __init__(self, db_connection):
        """
        :param db_connection: (postgres) data base connection
        """
        self.conn = db_connection

    def get_id_mapping_rows(self):
        raw_tuples = []

        cur = self.conn.cursor()
        cur.execute("SELECT species, entrez_id, refseq_id, symbol_id FROM {}".format(self.table_name))

        for species, entrez_id, refseq_id, symbol_id in cur.fetchall():
            raw_tuples.append((species, entrez_id, refseq_id, symbol_id))

        return raw_tuples


class GseTitlesDAO:
    def get_titles(self):
        """
        Returns dict {gse: title} from NCBI web-site
        :rtype dict
        """
        raise NotImplementedError()


class GseTitlesFileDAO(GseTitlesDAO):
    def __init__(self, path):
        """
        :type path: str
        """
        self.path = path

    def get_titles(self):
        titles = {}

        for line in [line.strip() for line in open(self.path).readlines()]:
            gse, title = line.split('\t')
            titles[gse] = title

        return titles


class GseTitlesSqlDAO(GseTitlesDAO):
    table_name = 'module_descriptions'

    def __init__(self, db_connection):
        """
        :param db_connection: (postgres) data base connection
        """
        self.conn = db_connection

    def get_titles(self):
        titles = {}

        cur = self.conn.cursor()
        cur.execute("SELECT series, title FROM {}".format(self.table_name))

        for series, title in cur.fetchall():
            titles[series] = title

        return titles