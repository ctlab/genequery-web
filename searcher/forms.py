from django import forms

from searcher.validators import entrez_id_validator, refseq_id_validator, symbol_id_validator
from utils import get_gene_id_type, ENTREZ, REFSEQ, SYMBOL
from searcher import models


SPECIES_REQUIRED = 'Species not specified.'
GENE_LIST_REQUIRED = 'Gene list is empty.'


class SearchQueryForm(forms.Form):
    species = forms.ChoiceField(models.SPECIES, required=True, error_messages={'required': SPECIES_REQUIRED})
    genes = forms.CharField(required=True, error_messages={'required': GENE_LIST_REQUIRED})

    genes_id_type = None

    def clean_genes(self):
        data = self.cleaned_data['genes']
        genes = data.split()
        id_type = get_gene_id_type(genes[0])
        if id_type == ENTREZ:
            id_validator = entrez_id_validator
        elif id_type == REFSEQ:
            id_validator = refseq_id_validator
        elif id_type == SYMBOL:
            id_validator = symbol_id_validator
        else:
            raise forms.ValidationError('Gene {} has unknown id type.'.format(genes[0]))
        for gene in genes:
            if isinstance(gene, unicode):
                raise forms.ValidationError('Use only digits and latin letters')
            t = get_gene_id_type(gene)
            if t != id_type:
                raise forms.ValidationError(
                    'Gene id types should be the same (both {} and {} are presents in query): {}'.format(id_type, t, gene))
            id_validator(gene)
        self.genes_id_type = id_type
        return genes

    def get_genes_id_type(self):
        return self.genes_id_type

    def get_error_messages_as_list(self):
        messages = []
        for m in self.errors.values():
            messages.append(m[0])
        return messages