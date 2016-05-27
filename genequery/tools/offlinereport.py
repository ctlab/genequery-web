import math

import fisher
import os
from collections import defaultdict


REPORT_TEMPLATES_DIR = './genequery/tools/templates/'


class DataSet:
    def __init__(self, name, species, path_to_gmt, path_to_titles):
        self.name = name
        self.species = species
        self._path_to_gmt = path_to_gmt

        self.gene_frequency = defaultdict(int)
        self.modules = defaultdict(set)
        self.gse_to_modules = defaultdict(list)
        self.gse_genes = defaultdict(set)

        self._gse_titles = dict([tuple(line.strip().split('\t')) for line in open(path_to_titles).readlines()])

        for module_name, genes in [line.strip().split('\t') for line in open(path_to_gmt).readlines()]:
            genes = set(map(int, genes.split(',')))
            gse = module_name.split('#')[0]

            for g in genes:
                self.gene_frequency[g] += 1

            self.modules[module_name] = genes
            self.gse_to_modules[gse].append(module_name)
            self.gse_genes[gse] |= genes

    def gse_title(self, gse):
        """
        :type gse: str
        """
        return self._gse_titles.get(gse.split('_')[0]) or self._gse_titles.get(gse) or 'No title'

    def __repr__(self):
        return '{},{},modules={},gses={}'.format(self.name, self.species, len(self.modules), len(self.gse_to_modules))


class MSigDBGeneset:
    def __init__(self, name, entrez_genes, species,
                 symbol_genes=None,
                 brief_description=None,
                 description=None):
        """
        Represents single geneset to be used as a query.

        :type name: str
        :type entrez_genes: iterable[int]
        :type species: str
        :type symbol_genes: iterable[str] or None
        :type brief_description: str or None
        :type description: str or None
        :return: MSigDBGeneset
        """
        self.name = name
        self.entrez_genes = set(entrez_genes)
        self.species = species
        self.symbol_genes = symbol_genes or set()
        self.description = description or 'No description'
        self.brief_description = brief_description or 'No description'

    def get_url(self):
        return 'http://software.broadinstitute.org/gsea/msigdb/cards/{}.html'.format(self.name)

    def __repr__(self):
        return '{}[{} genes,{}]'.format(self.name, len(self.entrez_genes), self.species)


class GenesetCollection:
    url = None
    name = None

    def __init__(self, species):  # TODO common species for all genesets in collection is bad design decision
        self.species = species
        self.genesets = {}

    def __repr__(self):
        return '{}({} gene sets)'.format(self.name, len(self.genesets))


class HallmarkCollection(GenesetCollection):
    name = 'Hallmark'
    url = 'http://software.broadinstitute.org/gsea/msigdb/genesets.jsp?collection=H'

    def __init__(self, path_to_entrez, path_to_symbol, path_to_description, species):
        GenesetCollection.__init__(self, species)

        for name, url, entrez_genes in [x.strip().split('\t', 2) for x in open(path_to_entrez).readlines()]:
            genes = set(map(int, entrez_genes.split('\t')))
            self.genesets[name] = MSigDBGeneset(name, genes, self.species)

        for name, brief_description in [x.strip().split('\t') for x in open(path_to_description).readlines()]:
            self.genesets[name].brief_description = brief_description

        for name, url, symbol_genes in [x.strip().split('\t', 2) for x in open(path_to_symbol).readlines()]:
            self.genesets[name].symbol_genes = set(symbol_genes.split('\t'))


class C7Collection(GenesetCollection):
    name = 'C7'
    url = 'http://software.broadinstitute.org/gsea/msigdb/genesets.jsp?collection=C7'

    def __init__(self, path_to_entrez, path_to_symbol, species):
        GenesetCollection.__init__(self, species)

        for name, gse, _, url, entrez_genes in [x.split('\t') for x in open(path_to_entrez).read().splitlines()]:
            genes = set(map(int, entrez_genes.split()))
            self.genesets[name] = MSigDBGeneset(name, genes, self.species)

        for name, url, symbol_genes in [x.split('\t', 2) for x in open(path_to_symbol).read().splitlines()]:
            if name in self.genesets:
                self.genesets[name].symbol_genes = set(symbol_genes.split('\t'))


class C2Collection(GenesetCollection):
    name = 'C2'
    url = 'http://software.broadinstitute.org/gsea/msigdb/genesets.jsp?collection=C2'

    def __init__(self, path_to_entrez, path_to_symbol, species):
        GenesetCollection.__init__(self, species)

        for name, entrez_genes in [x.split('\t') for x in open(path_to_entrez).read().splitlines()]:
            genes = set(map(int, entrez_genes.split(',')))
            self.genesets[name] = MSigDBGeneset(name, genes, self.species)

        for name, symbol_genes in [x.split('\t') for x in open(path_to_symbol).read().splitlines()]:
            if name in self.genesets:
                self.genesets[name].symbol_genes = set(symbol_genes.split(','))


class SearchResultItem:
    def __init__(self, module_full_name, log_p_value, intersection_size, module_size,
                 intersection_genes=None, gse_title=None, query_gse_intersection_size=None):
        """
        Represents single search result line (module).

        :type gse_title: str
        :type query_gse_intersection_size: int
        :type intersection_size: int
        :type log_p_value: float
        :type module_full_name: str
        :type intersection_genes: None or list[int]
        """
        self.log_p_value = log_p_value
        self.intersection_genes = intersection_genes
        self.intersection_size = intersection_size
        self.module_full_name = module_full_name
        self.module_size = module_size
        self.gse_name, module_number = module_full_name.split('#')
        self.module_number = int(module_number)
        self.gse_title = gse_title
        self.query_gse_intersection_size = query_gse_intersection_size

    def __cmp__(self, other):
        """
        Compare by log(Fisher p-value)
        """
        _d = self.log_p_value - other.log_p_value
        return _d / abs(_d) if _d != 0 else 0

    def __repr__(self):
        return '{},{},{}/{}/{}'.format(self.module_full_name, self.log_p_value,
                                       self.intersection_size, self.query_gse_intersection_size, self.module_size)


class SearchResultItemsGroup:
    def __init__(self, name, result_items, info=None, score=None):
        """
        :type name: str
        :type result_items: list[SearchResultItem]
        :type info: dict
        :type score: float
        """
        self.name = name
        self.result_items = sorted(result_items)
        self.info = info or {}
        self.score = score if score is not None else self.result_items[0].log_p_value

    def __repr__(self):
        return '{},{} items'.format(self.name, len(self.result_items))

    def __cmp__(self, other):
        _d = self.score - other.score
        return _d / abs(_d) if _d != 0 else 0


class GroupedSearchResult:
    def __init__(self, geneset, groups=None, result_info=None):
        """
        :type result_info: str or None
        :type groups: list[SearchResultItemsGroup]
        :type geneset: MSigDBGeneset
        """
        self.result_info = result_info or 'No info for this grouped search result'
        self.groups = groups or []
        self.geneset = geneset

    def total_results_number(self):
        return sum(len(group.result_items) for group in self.groups)


def fisher_right_tail(intersection_size, gse_size, query_size, module_size):
    """
    :type query_size: int
    :type gse_size: int
    :type intersection_size: int
    :type module_size: int
    """
    a = intersection_size
    b = module_size - a
    c = query_size - a
    d = gse_size - query_size - b
    return fisher.pvalue(a, b, c, d).right_tail


def make_simple_query(query, ds, log_cutoff=-7):
    """
    :type query: set of int
    :type ds: DataSet
    :type log_cutoff: int
    :rtype: list[dict]
    """
    result = []
    for gse_name, gse_genes in ds.gse_genes.items():
        adjusted_query_size = len(gse_genes & query)
        if adjusted_query_size == 0:
            continue
        for module_name in ds.gse_to_modules[gse_name]:
            if module_name.endswith('#0'):
                continue
            module_genes = ds.modules[module_name]
            intersection_size = len(module_genes & query)
            if intersection_size == 0:
                continue
            pvalue = fisher_right_tail(intersection_size, len(gse_genes), adjusted_query_size, len(module_genes))
            log_pvalue = -325 if pvalue == 0 else math.log10(pvalue)
            if log_pvalue > log_cutoff:
                continue
            result.append({
                'module_name': module_name,
                'log_p_value': log_pvalue,
                'intersection_size': intersection_size,
                'module_size': len(module_genes),
                'intersection_query_gse_size': adjusted_query_size,
                'gse_title': ds.gse_title(gse_name)
            })
    return result


def render_and_write(path, template, context):
    """
    :type template: jinja2.Template
    :type path: str
    :type context: dict
    """
    with open(path, 'w') as fd:
        fd.write(template.render(**context))


def render_report(grouped_search_result, destination_folder, geneset_collection, experiment_description=None):
    """
    :type experiment_description: str
    :type geneset_collection: GenesetCollection
    :type destination_folder: str
    :type grouped_search_result: list[GroupedSearchResult]
    """
    import sys
    from jinja2 import Environment, FileSystemLoader
    reload(sys)
    sys.setdefaultencoding('utf-8')

    env = Environment(loader=FileSystemLoader(REPORT_TEMPLATES_DIR))

    if not os.path.exists(destination_folder):
        os.mkdir(destination_folder)
    else:
        print 'Folder {} already exists, results will be overwritten'.format(destination_folder)

    # create index file
    render_and_write(
        os.path.join(destination_folder, 'index.html'),
        env.get_template('searchresult/index.html'),
        {
            'experiment_description': experiment_description,
            'active': 'index',
            'collection': geneset_collection,
            'search_results': grouped_search_result,
        }
    )

    for curr_search_result in grouped_search_result:
        try:
            render_and_write(
                os.path.join(
                    destination_folder,
                    '{}_{}.html'.format(curr_search_result.geneset.name, curr_search_result.geneset.species)),
                env.get_template('searchresult/result.html'),
                {
                    'collection': geneset_collection,
                    'active': curr_search_result.geneset.name,
                    'search_results': grouped_search_result,
                    'curr_search_result': curr_search_result,
                }
            )
        except Exception, e:
            print e
            for g in curr_search_result.groups:
                print g, g.result_items