from django import forms
from django.core.exceptions import ValidationError

from genequery.utils.constants import *

SPECIES_CHOICES = (
    (HS, 'Homo Sapiens'),
    (MM, 'Mus Musculus'),
    (RT, 'Rattus Norvegicus'),
)


DB_SPECIES_REQUIRED = 'Data base species are not specified.'
QUERY_SPECIES_REQUIRED = 'Query genes species are not specified.'
GENE_LIST_REQUIRED = 'Gene list is empty.'


class SearchQueryForm(forms.Form):
    db_species = forms.ChoiceField(SPECIES_CHOICES,
                                   required=True,
                                   error_messages={'required': DB_SPECIES_REQUIRED})
    query_species = forms.ChoiceField(SPECIES_CHOICES,
                                      required=True,
                                      error_messages={'required': QUERY_SPECIES_REQUIRED})
    genes = forms.CharField(required=True, error_messages={'required': GENE_LIST_REQUIRED})

    genes_id_type = None

    def clean_genes(self):
        """
        :returns genes as str in upper case
        :rtype: list of str
        """
        data = self.cleaned_data['genes']
        genes = data.split()

        for gene in genes:
            try:
                str(gene)
            except:
                raise forms.ValidationError('Can not parse one of the input genes. Use only latin letters.')

        return genes

    def get_error_messages_as_list(self):
        """
        :rtype: list of str
        """
        messages = []
        for m in self.errors.values():
            messages.append(m[0])
        return messages