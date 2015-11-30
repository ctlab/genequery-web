from django import forms
from django.core.exceptions import ValidationError

from genequery.searcher.idconvertion import get_gene_id_type
from genequery.searcher.models import ENTREZ_ID_MAX_LENGTH, REFSEQ_ID_MAX_LENGTH, SYMBOL_ID_MAX_LENGTH, SPECIES_CHOICES, \
    ENSEMBL_ID_MAX_LENGTH
from genequery.utils.constants import *


SPECIES_REQUIRED = 'Species are not specified.'
GENE_LIST_REQUIRED = 'Gene list is empty.'


def entrez_id_validator(value):
    if len(value) > ENTREZ_ID_MAX_LENGTH:
        raise ValidationError('Entrez id {} is too long.'.format(value))


def refseq_id_validator(value):
    if len(value) > REFSEQ_ID_MAX_LENGTH:
        raise ValidationError('RefSeq id {} is too long.'.format(value))


def symbol_id_validator(value):
    if len(value) > SYMBOL_ID_MAX_LENGTH:
        raise ValidationError('Symbol id {} is too long.'.format(value))


def ensembl_id_validator(value):
    if len(value) > ENSEMBL_ID_MAX_LENGTH:
        raise ValidationError('Ensembl id {} is too long.'.format(value))


class SearchQueryForm(forms.Form):
    species = forms.ChoiceField(SPECIES_CHOICES, required=True, error_messages={'required': SPECIES_REQUIRED})
    genes = forms.CharField(required=True, error_messages={'required': GENE_LIST_REQUIRED})

    genes_id_type = None

    def clean_genes(self):
        """
        :returns genes as str in upper case
        :rtype: list of str
        """
        data = self.cleaned_data['genes']
        genes = data.split()

        #  Calculate input id type by first gene
        first_gene = genes[0]
        first_gene_type = get_gene_id_type(first_gene)

        if first_gene_type == ENTREZ:
            id_validator = entrez_id_validator
        elif first_gene_type == REFSEQ:
            id_validator = refseq_id_validator
        elif first_gene_type == SYMBOL:
            id_validator = symbol_id_validator
        elif first_gene_type == ENSEMBL:
            id_validator = ensembl_id_validator
        else:
            raise forms.ValidationError('Gene {} has unknown id type.'.format(genes[0]))

        for gene in genes:
            try:
                str(gene)
            except:
                raise forms.ValidationError('Can not parse one of the input genes. Use only latin letters.')

            current_gene_type = get_gene_id_type(gene)
            if current_gene_type != first_gene_type:
                raise forms.ValidationError(
                    'Gene id types should be the same (both {}({}) and {}({}) are presents in query).'.format(
                        first_gene_type, first_gene, current_gene_type, gene
                    )
                )
            id_validator(gene)

        self.genes_id_type = first_gene_type
        return genes

    def get_genes_id_type(self):
        """
        :rtype: str
        """
        return self.genes_id_type

    def get_error_messages_as_list(self):
        """
        :rtype: list of str
        """
        messages = []
        for m in self.errors.values():
            messages.append(m[0])
        return messages