# coding=utf-8
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.html import escape
from djorm_pgarray.fields import IntegerArrayField
from genequery.utils.constants import ENTREZ, SYMBOL, REFSEQ, HS, MM, RT


MODULE_NAME_MAX_LENGTH = 50
SERIES_NAME_MAX_LENGTH = 50
ENTREZ_ID_MAX_LENGTH = 50
REFSEQ_ID_MAX_LENGTH = 50
ENSEMBL_ID_MAX_LENGTH = 100
OTHER_ID_MAX_LENGTH = 100
SYMBOL_ID_MAX_LENGTH = 50
SPECIES_MAX_LENGTH = 50


SPECIES_CHOICES = (
    (HS, 'Homo Sapiens'),
    (MM, 'Mus Musculus'),
    (RT, 'Rattus Norvegicus'),
)


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


class Refseq2Entrez(models.Model):
    species = models.CharField(u'Species', max_length=SPECIES_MAX_LENGTH, blank=False, choices=SPECIES_CHOICES)
    entrez_id = models.BigIntegerField(u'Entrez ID')
    refseq_id = models.CharField(u'RefSeq ID', max_length=REFSEQ_ID_MAX_LENGTH, db_index=True)

    class Meta:
        verbose_name = 'refseq2entrez map'
        verbose_name_plural = 'refseq2entrez maps'
        db_table = 'refseq_to_entrez'
        unique_together = (('species', 'refseq_id', 'entrez_id'),)

    def __unicode__(self):
        return u'{}(entrez={}, refseq={})'.format(self.species, self.entrez_id, self.refseq_id)


class Ensembl2Entrez(models.Model):
    species = models.CharField(u'Species', max_length=SPECIES_MAX_LENGTH, blank=False, choices=SPECIES_CHOICES)
    entrez_id = models.BigIntegerField(u'Entrez ID')
    ensembl_id = models.CharField(u'Ensembl ID', max_length=ENSEMBL_ID_MAX_LENGTH, db_index=True)

    class Meta:
        verbose_name = 'ensembl2entrez map'
        verbose_name_plural = 'ensembl2entrez maps'
        db_table = 'ensembl_to_entrez'
        unique_together = (('species', 'ensembl_id', 'entrez_id'),)

    def __unicode__(self):
        return u'{}(entrez={}, ensembl={})'.format(self.species, self.entrez_id, self.ensembl_id)


class Symbol2Entrez(models.Model):
    species = models.CharField(u'Species', max_length=SPECIES_MAX_LENGTH, blank=False, choices=SPECIES_CHOICES)
    entrez_id = models.BigIntegerField(u'Entrez ID', db_index=True)
    symbol_id = models.CharField(u'Symbol ID', max_length=SYMBOL_ID_MAX_LENGTH, db_index=True)

    class Meta:
        verbose_name = 'symbol2entrez map'
        verbose_name_plural = 'symbol2entrez maps'
        db_table = 'symbol_to_entrez'
        unique_together = (('species', 'symbol_id', 'entrez_id'),)

    def __unicode__(self):
        return u'{}(entrez={}, symbol={})'.format(self.species, self.entrez_id, self.symbol_id)


class Other2Entrez(models.Model):
    species = models.CharField(u'Species', max_length=SPECIES_MAX_LENGTH, blank=False, choices=SPECIES_CHOICES)
    entrez_id = models.BigIntegerField(u'Entrez ID', db_index=True)
    other_id = models.CharField(u'Other ID', max_length=SYMBOL_ID_MAX_LENGTH, db_index=True)

    class Meta:
        verbose_name = 'other2entrez map'
        verbose_name_plural = 'other2entrez maps'
        db_table = 'other_to_entrez'
        unique_together = (('species', 'other_id', 'entrez_id'),)

    def __unicode__(self):
        return u'{}(entrez={}, other={})'.format(self.species, self.entrez_id, self.other_id)


class Homologene(models.Model):
    group_id = models.PositiveIntegerField(u'Group ID', db_index=True)
    species = models.CharField(u'Species', max_length=SPECIES_MAX_LENGTH, blank=False, choices=SPECIES_CHOICES)
    entrez_id = models.BigIntegerField(u'Entrez ID', db_index=True)
    symbol_id = models.CharField(u'Symbol ID', max_length=SYMBOL_ID_MAX_LENGTH, db_index=True)
    refseq_id = models.CharField(u'RefSeq ID', max_length=REFSEQ_ID_MAX_LENGTH, db_index=True)

    class Meta:
        verbose_name = 'homologene'
        verbose_name_plural = 'homologenes'
        db_table = 'homologene'
        unique_together = (('group_id', 'species', 'entrez_id', 'symbol_id', 'refseq_id'),)

    def __unicode__(self):
        return u'group {},{}(entrez={},symbol={},refseq={})'.format(
            self.group_id, self.species, self.entrez_id, self.symbol_id, self.refseq_id)


def get_gse_info(gse_gpl_name):
    """
    :type gse_gpl_name: str
    :rtype: dict
    """
    gq_modules = GQModule.objects.filter(full_name__startswith=gse_gpl_name)
    if not gq_modules:
        return None
    info = {'gse': gse_gpl_name,
            'module_genes': {},
            'module_len': {},
            'all_genes': [],
            'total_modules': len(gq_modules)}
    for m in gq_modules:
        num = m.split_full_name()[-1]
        info['module_len'][num] = len(m.entrez_ids)
        info['module_genes'][num] = m.entrez_ids
        info['all_genes'] += m.entrez_ids

    return info