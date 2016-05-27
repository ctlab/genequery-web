from genequery.searcher.idconvertion import ToSymbolConversion
from genequery.searcher.models import GQModule
from genequery.utils import here
import numpy as np
import math
import matplotlib.pyplot as plt
from scipy.stats import hypergeom
import random
import os

GSEA_SETS_PATH = '/Users/smolcoder/ifmo/genequery-web/data/gsea_msigdb_collection/'

PATH_TO_DB_FILES = {
    2015: '/Users/smolcoder/ifmo/genequery-db/2015/original',
    2013: '/Users/smolcoder/ifmo/genequery-db/2013/original',
}


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
        gg = gse  # + '_' + gpl
        if gg not in gses:
            gses[gg] = set()
        gses[gg] |= set(module.entrez_ids)
    return gses


def get_gene_to_freq(path_to_file=None, db_version=None, species=None):
    if path_to_file:
        data = [x.strip().split('\t') for x in open(path_to_file).readlines()]
    elif db_version and species:
        data = [x.strip().split('\t')
                for x in open(here(PATH_TO_DB_FILES[db_version], '{}.freq.entrez.txt'.format(species))).readlines()]
    else:
        raise Exception('Specify path to file or db_version and species.')
    return {int(gene): int(freq) for gene, freq in data}


def intersect_with_each_gse_module(species, gse, query):
    query = set(query)
    res = {}
    for m in GQModule.objects.filter(species=species, full_name__startswith=gse):
        res[m.full_name] = (len(query & set(m.entrez_ids)), len(m.entrez_ids))
    return res


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


def read_queries(path):
    queries = [l.strip().split('\t') for l in open(path).readlines()]
    return {q[0]: set(map(int, q[-1].split())) for q in queries}


def read_modules(species):
    modules = dict(GQModule.objects.filter(species=species).values_list('full_name', 'entrez_ids'))
    for k in modules:
        modules[k] = set(modules[k])
    return modules


queries = read_queries(here(GSEA_SETS_PATH, 'hs.c7.queries.txt'))

mm_gses = get_all_gses('mm')
hs_gses = get_all_gses('hs')
rt_gses = get_all_gses('rt')

hs_gene2freq = get_gene_to_freq(db_version=2015, species='hs')
mm_gene2freq = get_gene_to_freq(db_version=2015, species='mm')
rt_gene2freq = get_gene_to_freq(db_version=2015, species='rt')

hs_modules = read_modules('hs')
mm_modules = read_modules('mm')
rt_modules = read_modules('rt')


class QueryResultItem:
    def __init__(self, qid, rank, line):
        self.rank = rank
        self.qid = qid

        module_name, a, b, c, d, pv, log_pv, genes = line.strip().split('\t')
        self.module_name = module_name
        self.a, self.b, self.c, self.d = int(a), int(b), int(c), int(d)
        self.pv, self.logPv = float(pv), float(log_pv)
        self.intersection_genes = map(int, genes.split())

        self.gse = module_name.split('_')[0]

    def __repr__(self):
        return '[{}]{} ({},{},{},{}) logPv={}, inter_len={}'.format(
            self.rank, self.module_name, self.a, self.b, self.c, self.d, self.logPv, len(self.intersection_genes))


result_path = here(GSEA_SETS_PATH, 'searchresults', 'h')
query_results = {}
for f in os.listdir(result_path):
    qid = f.split('.')[0]
    res = [QueryResultItem(qid, i + 1, line)
           for i, line in enumerate(open(here(result_path, f)).readlines())]
    if len(res):
        query_results[qid] = res

qids = sorted(query_results.keys(), key=lambda x: len(query_results[x]), reverse=True)


def get_common_gses(qids, gses):
    return set(set([q.split('_')[0] for q in qids])) & set(gses.keys())


def get_rare_count(genes):
    return float(len([g for g in genes if gene2freq[g] < 500]))


COMMON_GSES = get_common_gses(qids, mm_gses)


def idf(genes):
    return sum([math.log(3900. / gene2freq[g], 2) for g in genes])


stat = {i: [] for i in range(1, 101)}
for q in qids:
    if 100 <= len(query_results[q]) <= 1000:
        continue
    for r in query_results[q][:100]:
        stat[r.rank].append(idf(r.intersection_genes) / len(r.intersection_genes))

res = query_results[qids[10]]
plt.scatter(np.arange(len(res)), [idf(r.intersection_genes) / len(r.intersection_genes) for r in res])


def sign(gene_freq, scale):
    # return float(3900 - gene_freq + 1) / scale
    # return 15177 / (gene_freq + 674) - 2.5
    if 1 <= gene_freq <= 500:
        return 3
    if 500 <= gene_freq <= 2000:
        return 2
    if 2000 <= gene_freq <= 3000:
        return 2
    return 0.8


def bump_genes(genes, scale):
    return sum([sign(g, scale) for g in genes])


def new_f_table(query_genes, module_genes, gse_genes, scale=100):
    x = bump_genes(query_genes & module_genes, scale)
    M = bump_genes(gse_genes, scale)
    n = bump_genes(query_genes & gse_genes, scale)
    N = bump_genes(module_genes, scale)
    return x, M, n, N


def calc_f_table(x, M, n, N):
    return hypergeom.logsf(x, M, n, N) / math.log(10)


x, y1, y2 = [], [], []
for r in query_results['GSE40274_CTRL_VS_FOXP3_AND_LEF1_TRANSDUCED_ACTIVATED_CD4_TCELL_UP'][:700]:
    x.append(r.rank)
    q_genes = set(queries[r.qid])
    gse_genes = mm_gses[r.gse]
    m_genes = set(GQModule.objects.get(full_name=r.module_name).entrez_ids)
    nft = new_f_table(q_genes, m_genes, gse_genes, scale=250)
    y1.append(-calc_f_table(*nft))
    y2.append(-r.logPv)
    if r.gse == r.qid.split('_')[0]:
        print r.rank - 1, y1[-1], y2[-1]
# plt.subplot(131)
# plt.scatter(x, y1)
# plt.subplot(132)
# plt.scatter(x, sorted(y1, reverse=True))
# plt.subplot(133)
# plt.scatter(x, y2)


for q in qids:
    gse = q.split('_')[0]
    inds = [r.rank for r in query_results[q] if r.gse == gse]
    if len(inds) > 1 or (len(inds) == 1 and inds[0] > 1):
        print len(inds), q, inds

cancer_gses = set([x.strip() for x in open(here(GSEA_SETS_PATH, 'cancer_hs_gses.txt')).readlines()])

top = 50

nqids = query_results.keys()
random.shuffle(nqids)

new_results = {}
pss = []
accs = []
for pos, q in enumerate(nqids[:350]):
    new_results[q] = []
    ps = 0.
    acc = 0.
    for r in query_results[q][:500]:
        q_genes = queries[r.qid]
        gse_genes = hs_gses[r.gse]
        m_genes = hs_modules[r.module_name]
        nft = new_f_table(q_genes, m_genes, gse_genes, scale=250)
        new_value = calc_f_table(*nft)
        new_results[q].append((r.gse, new_value))
    new_results[q] = sorted(new_results[q], key=lambda x: x[-1])
    for rank, r in enumerate(new_results[q][:top]):
        if r[0] in cancer_gses:
            ps += 1. / (rank + 1)
            acc += 1
    pss.append(ps)
    accs.append(acc / min(top, len(new_results[q])))
    # print pos + 1, np.mean(pss), np.std(pss)
    print pos + 1, np.mean(accs), np.std(accs)

pss = []
accs = []
for q in nqids[:185]:
    ps = 0.
    acc = 0.
    for r in query_results[q][:top]:
        if r.gse in cancer_gses:
            ps += 1. / r.rank
            acc += 1
    pss.append(ps)
    accs.append(acc / min(top, len(query_results[q])))
# print np.mean(pss), np.std(pss)
print np.mean(accs), np.std(accs)


rare = set([g for g, f in rt_gene2freq.items() if f <= 10])
d = {}
for g in rt_gses:
    d[g] = len(rt_gses[g] & rare)

for g in sorted(d.keys(), key=d.get, reverse=True)[:20]:
    print g
plt.scatter(np.arange(len(d)), sorted(d.values(), reverse=True))


def idf(freqs, max_freq):
    return sum([math.log(float(max_freq) / f, 2) for f in freqs]) / len(freqs)


def foo(qid):
    plt.figure(figsize=(15, 7))
    plt.subplot(311)
    plt.plot([-r.logPv for r in query_results[qids[25]]])
    plt.subplot(312)
    plt.plot([idf(r.intersection_genes) for r in query_results[qids[25]]])
    plt.subplot(313)
    plt.plot([len(r.intersection_genes) for r in query_results[qids[25]]])

foo(qids[25])

x, y = [], []
y1 = []
for r in query_results[qids[15]]:
    x.append(len(r.intersection_genes))
    y.append(idf(r.intersection_genes))
    y1.append(-r.logPv)
plt.subplot(311)
plt.scatter(x, y)
plt.subplot(312)
plt.scatter(x, y1)
plt.subplot(313)
plt.scatter(y1, y)

a = []
for qid, qgenes in queries.items():
    freqs = sorted([hs_gene2freq.get(g, 0) for g in qgenes])
    freqs = filter(lambda f: f > 0, freqs)
    rare_count = len(filter(lambda f: f < 380, freqs)) * 1.
    a.append(freqs)
    # if rare_count / len(freqs) >= 0.4:
    #     print '{}\t{}\t{}\t{}'.format(qid, len(freqs), rare_count / len(freqs), freqs)
        # print '{}\t{}'.format(qid, rare_count / len(freqs))
a = np.array(a)
a.sort(axis=0)
x, y = [], []
for i in a:
    x.append((len(filter(lambda j: j < 380, i)) + 1) / float(len(i)))
    y.append(idf(i, 5365))
    print x[-1], y[-1], i
plt.scatter(x, y)
plt.xlabel('Part of rare (within 50% percentile) genes')
plt.ylabel('idf')
plt.title('C7 (immunologic) gene sets. Human.')
plt.savefig('/Users/smolcoder/statistics/img/idf_of_rare_ratio_c7_hs.png', dpi=300)