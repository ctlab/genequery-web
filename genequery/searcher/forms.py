from django import forms
from django.core.exceptions import ValidationError

from genequery.searcher.idconvertion import get_gene_id_type
from genequery.searcher.models import ENTREZ_ID_MAX_LENGTH, REFSEQ_ID_MAX_LENGTH, SYMBOL_ID_MAX_LENGTH, SPECIES_CHOICES, \
    ENSEMBL_ID_MAX_LENGTH
from genequery.utils.constants import *


DB_SPECIES_REQUIRED = 'Data base species are not specified.'
QUERY_SPECIES_REQUIRED = 'Query genes species are not specified.'
GENE_LIST_REQUIRED = 'Gene list is empty.'


def entrez_id_validator(value):
    if len(value) > ENTREZ_ID_MAX_LENGTH:
        raise ValidationError('Entrez id {} is too long. Less than {} characters is expected.'.format(
            value, ENTREZ_ID_MAX_LENGTH))


def refseq_id_validator(value):
    if len(value) > REFSEQ_ID_MAX_LENGTH:
        raise ValidationError('RefSeq id {} is too long. Less than {} characters is expected'.format(
            value, REFSEQ_ID_MAX_LENGTH))


def symbol_id_validator(value):
    if len(value) > SYMBOL_ID_MAX_LENGTH:
        raise ValidationError('Symbol id {} is too long. Less than {} characters is expected'.format(
            value, SYMBOL_ID_MAX_LENGTH))


def ensembl_id_validator(value):
    if len(value) > ENSEMBL_ID_MAX_LENGTH:
        raise ValidationError('Ensembl id {} is too long. Less than {} characters is expected.'.format(
            value, ENSEMBL_ID_MAX_LENGTH))


class SearchQueryForm(forms.Form):
    db_species = forms.ChoiceField(SPECIES_CHOICES, required=True, error_messages={'required': DB_SPECIES_REQUIRED})
    query_species = forms.ChoiceField(SPECIES_CHOICES, required=True, error_messages={'required': QUERY_SPECIES_REQUIRED})
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
                    'Gene id types should be the same. Both {} ({}) and {} ({}) are presents in query.'.format(
                        first_gene_type, first_gene, current_gene_type, gene
                    )
                )
            id_validator(gene)

        self.genes_id_type = first_gene_type
        return genes

    # def get_original_to_clean_genes_dict(self):
    #     """
    #     :rtype: dict[str, str]
    #     """
    #     genes = self.cleaned_data['genes']
    #     query_species = self.cleaned_data['query_species']
    #     notation_type = self.get_genes_id_type()
    #
    #     res = {}
    #     for gene in genes:
    #         gene_original = gene
    #         # remove the first dot and the rest after it
    #         if notation_type in [REFSEQ, ENSEMBL] and '.' in gene:
    #             gene = gene[:gene.find('.')]
    #         # change register according to query species
    #         if notation_type == SYMBOL:
    #             if query_species in [MM, RT]:
    #                 gene = gene.capitalize()
    #             else:
    #                 gene = gene.upper()
    #         if notation_type == ENTREZ:
    #             gene = int(gene)
    #         res[gene_original] = gene
    #
    #     return res

    # def get_genes_id_type(self):
    #     """
    #     :rtype: str
    #     """
    #     return self.genes_id_type

    def get_error_messages_as_list(self):
        """
        :rtype: list of str
        """
        messages = []
        for m in self.errors.values():
            messages.append(m[0])
        return messages