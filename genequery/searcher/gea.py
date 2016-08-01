class EnrichmentResultItem:
    def __init__(self, gse, gpl, module_number, module_size, intersection_size, species,
                 pvalue, log10_pvalue, adj_pvalue, log10_adj_pvalue):
        """
        :type intersection_size: int
        :type pvalue: float
        :type log10_pvalue: float
        :type adj_pvalue: float
        :type log10_adj_pvalue: float
        :type gse: str
        :type gpl: str
        :type module_number: int
        :type module_size: int
        :type species: str
        """
        self.species = species
        self.gse = gse
        self.gpl = gpl
        self.module_number = module_number
        self.module_size = module_size
        self.intersection_size = intersection_size
        self.pvalue = pvalue
        self.log_pvalue = log10_pvalue
        self.adj_p_value = adj_pvalue
        self.log_adj_p_value = log10_adj_pvalue

    def __cmp__(self, other):
        if self.log_pvalue == other.log_pvalue:
            return 0
        return 1 if self.log_pvalue > other.log_pvalue else -1

    def __repr__(self):
        return 'EnrichmentResultItem[gse={},gpl={},#module={},inters={},lg(adj-p-value)={}'.format(
            self.gse, self.gpl, self.module_number, self.intersection_size, self.log_adj_p_value)