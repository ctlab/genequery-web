# coding=utf-8
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.html import escape
from djorm_pgarray.fields import IntegerArrayField
from utils.constants import ENTREZ, SYMBOL, REFSEQ, HS, MM, RT


MODULE_NAME_MAX_LENGTH = 50
SERIES_NAME_MAX_LENGTH = 50
ENTREZ_ID_MAX_LENGTH = 50
REFSEQ_ID_MAX_LENGTH = 50
SYMBOL_ID_MAX_LENGTH = 50
SPECIES_MAX_LENGTH = 50


SPECIES_CHOICES = (
    (HS, 'Homo Sapiens'),
    (MM, 'Mus Musculus'),
    (RT, 'Rattus Norvegicus'),
)


# Run-time modules cache
SPECIES_TO_MODULES_CACHE = {}


class GQModule(models.Model):
    species = models.CharField(u'Species', max_length=SPECIES_MAX_LENGTH, blank=False, choices=SPECIES_CHOICES)

    full_name = models.CharField(u'Module',
                                 max_length=MODULE_NAME_MAX_LENGTH,
                                 primary_key=True,
                                 blank=False,
                                 help_text=escape(
                                     u'Module name specified as <series name>_<platform name>#<module number>'))

    entrez_ids = IntegerArrayField(verbose_name="Entrez IDs", dimension=1, blank=False,
                                   help_text=u'Entrez IDs of genes contained in this module. '
                                             u'Should be separated by comma.')

    def split_full_name(self):
        """
        :rtype: str, str, int
        """
        gse_gpl, module_number = self.full_name.split('#')
        gse, gpl = gse_gpl.split('_')
        return gse, gpl, int(module_number)

    @staticmethod
    def get_modules(species):
        """
        :type species: str
        """
        if species not in SPECIES_TO_MODULES_CACHE:
            print 'Push to cache', species
            SPECIES_TO_MODULES_CACHE[species] = [m for m in GQModule.objects.filter(species=species)]
        return SPECIES_TO_MODULES_CACHE[species]

    @staticmethod
    def merge_full_name(gse, gpl, module_number):
        """
        Create full module name like GSE_GPL#module_number
        :type module_number: int
        :type gpl: str
        :type gse: str
        :rtype str
        """
        return '{}_{}#{}'.format(gse, gpl, module_number)

    class Meta:
        verbose_name = 'Module'
        verbose_name_plural = 'Modules'
        db_table = 'modules'
        unique_together = (('species', 'full_name'),)

    def __unicode__(self):
        id_module = self.full_name.split('#')
        series_platform = id_module[0].split('_')
        return u'series {} platform {} module {} ({})'.format(
            series_platform[0], series_platform[1], id_module[1], self.species)


class ModuleDescription(models.Model):
    series = models.CharField(u'Series ID', max_length=SERIES_NAME_MAX_LENGTH, primary_key=True)
    title = models.TextField(null=True)

    @staticmethod
    def get_title_or_default(gse, default):
        try:
            return ModuleDescription.objects.get(series=gse).title
        except ObjectDoesNotExist:
            return default

    class Meta:
        db_table = 'module_descriptions'

    def __unicode__(self):
        return u'[{}] {}'.format(self.series, self.title)


class IdMap(models.Model):
    species = models.CharField(u'Species', max_length=SPECIES_MAX_LENGTH, blank=False, choices=SPECIES_CHOICES)
    entrez_id = models.BigIntegerField(u'Entrez ID', blank=False)
    refseq_id = models.CharField(u'RefSeq ID', max_length=REFSEQ_ID_MAX_LENGTH, null=True, blank=True)
    symbol_id = models.CharField(u'Symbol ID', max_length=SYMBOL_ID_MAX_LENGTH, null=True, blank=True)

    @staticmethod
    def convert_to_entrez(species, notation_type, uppercase_genes):
        """
        Convert genes to entrez notation.
        Returns list of pairs where every pair is tuple of two values:
            entrez ID and original ID for every gene from input genes.

        :type uppercase_genes: list of (int or str)
        :type notation_type: str
        :type species: str
        :rtype: list of (int, int or str)
        :returns list of pairs: (entrez ID, original gene ID)
        """
        if notation_type == ENTREZ:
            #  No mapping is required
            return list(set([(int(g), g) for g in uppercase_genes]))

        uppercase_genes = set(uppercase_genes)

        if notation_type == SYMBOL:
            kwargs = {'symbol_id__in': uppercase_genes}
        elif notation_type == REFSEQ:
            kwargs = {'refseq_id__in': uppercase_genes}
        else:
            raise Exception('Unknown notation type: {}'.format(notation_type))

        return list(set(IdMap.objects
                        .filter(species=species)
                        .filter(**kwargs)
                        .values_list('entrez_id', notation_type + '_id')))

    class Meta:
        verbose_name = 'id map'
        verbose_name_plural = 'id maps'
        db_table = 'id_map'
        unique_together = (('species', 'refseq_id', 'symbol_id'),)

    def __unicode__(self):
        return u'{}(entrez={}, refseq={}, symbol={})'.format(
            self.species, self.entrez_id, self.refseq_id or 'None', self.symbol_id or 'None')
