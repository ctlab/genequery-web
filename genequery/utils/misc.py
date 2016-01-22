from genequery.searcher.idconvertion import ToSymbolConversion
from genequery.searcher.models import GQModule
from genequery.utils import here
import numpy as np
import matplotlib.pyplot as plt


def gmt_entrez_to_symbol(path_from, path_to, species):
    data = [line.strip().split('\t') for line in open(path_from).readlines()]
    out = open(path_to, 'w')
    for name, entrez_ids in data:
        entrez_ids = map(int, entrez_ids.split(','))
        result = ToSymbolConversion.convert(species, 'entrez', entrez_ids)
        symbol_ids = result.get_final_symbol_ids()
        out.write('{}\t{}\n'.format(name, ','.join(symbol_ids)))


def get_gse_genes(gse, gpl=None, species=None):
    qs = GQModule.objects.filter(full_name__startswith='{}_'.format(gse))
    if gpl:
        qs = qs.filter(full_name__startswith='{}_{}'.format(gse, gpl))
    if species:
        qs = qs.filter(species=species)

    genes = []
    gses = set()
    speciess = set()
    for m in qs.all():
        gse, gpl, num = m.split_full_name()
        gses.add(gse + '_' + gpl)
        speciess.add(m.species)
        genes += m.entrez_ids

    if len(gses) > 1:
        raise Exception("There's more than one different GSEs: {}".format(','.join(gses)))
    if len(speciess) > 1:
        raise Exception("There's more than one different species: {}".format(','.join(speciess)))
    if not genes:
        raise Exception("GSE not found")
    return list(set(genes))


def get_all_gses(species):
    gses = {}
    for module in GQModule.objects.filter(species=species):
        gse, gpl, module_number = module.split_full_name()
        if (gse, gpl) not in gses:
            gses[(gse, gpl)] = set()
        gses[(gse, gpl)] |= set(module.entrez_ids)
    return gses


PATH_TO_DB_FILES = {
    2015: '/Users/smolcoder/ifmo/genequery-db/2015/original',
    2013: '/Users/smolcoder/ifmo/genequery-db/2013/original',
}


def get_gene_to_freq(path_to_file=None, db_version=None, species=None):
    if path_to_file:
        data = [x.strip().split('\t') for x in open(path_to_file).readlines()]
    elif db_version and species:
        data = [x.strip().split('\t')
                for x in open(here(PATH_TO_DB_FILES[db_version], '{}.freq.entrez.txt'.format(species))).readlines()]
    else:
        raise Exception('Specify path to file or db_version and species.')
    return {int(gene): int(freq) for gene, freq in data}


def create_pretty_gmt(outpath):
    print 'Collecting data'
    gses = {}
    for iter, m in enumerate(GQModule.objects.all()):
        if iter % 1000 == 0:
            print iter, 'modules done'
        gse, gpl, num = m.split_full_name()
        key = gse + '_' + gpl
        if key not in gses:
            gses[key] = {}
        gses[key][num] = ToSymbolConversion.convert(m.species, 'entrez', m.entrez_ids).get_final_symbol_ids()
        # if len(gses[key][num]) != len(m.entrez_ids):
        #     print '{}: {} != {}'.format(key, len(gses[key][num]), len(m.entrez_ids))

    print 'Writing results to', outpath
    for gse in gses:
        out = open(here(outpath, gse + '.gmt'), 'w')
        for num in range(0, len(gses[gse])):
            out.write('{}\t{}\n'.format(num, ' '.join(gses[gse][num])))