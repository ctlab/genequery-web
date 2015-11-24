# coding=utf-8
"""
This module is commented since we don't use DB for now.
Instead we pre-load data from files and store it in RAM to make this
web service as simple as possible.
"""
from django.db import models
# from django.utils.html import escape
# from djorm_pgarray.fields import IntegerArrayField
# from common.constants import *
#
#
# class ModuleGenes(models.Model):
#     species = models.CharField(u'Species', max_length=SPECIES_MAX_LENGTH, blank=False, choices=SPECIES_CHOICES)
#
#     module = models.CharField(u'Module',
#                               max_length=MODULE_NAME_MAX_LENGTH,
#                               primary_key=True,
#                               blank=False,
#                               help_text=escape(u'Module name specified as <series name>_<platform name>#<module number>'))
#
#     entrez_ids = IntegerArrayField(verbose_name="Entrez IDs", dimension=1, blank=False,
#                                    help_text=u'Entrez IDs of genes contained in this module. '
#                                              u'Should be separated by comma.')
#
#     class Meta:
#         db_table = 'module_genes'
#         unique_together = (('species', 'module'),)
#
#     def __unicode__(self):
#         id_module = self.module.split('#')
#         series_platform = id_module[0].split('_')
#         return u'series {} platform {} module {} ({})'.format(
#             series_platform[0], series_platform[1], id_module[1], self.species)
#
#
# class ModuleDescription(models.Model):
#     series = models.CharField(u'Series ID', max_length=SERIES_NAME_MAX_LENGTH, primary_key=True)
#     status = models.CharField(max_length=100, null=True)
#     title = models.TextField(null=True)
#     organisms = models.CharField(max_length=100, null=True)
#     overall_design = models.TextField(null=True)
#     summary = models.TextField(null=True)
#     experiment_type = models.TextField(null=True)
#
#     class Meta:
#         db_table = 'module_descriptions'
#
#     def __unicode__(self):
#         return u'[{}] {}'.format(self.series, self.title)
#
#
# class IdMap(models.Model):
#     species = models.CharField(u'Species', max_length=SPECIES_MAX_LENGTH, blank=False, choices=SPECIES_CHOICES)
#     entrez_id = models.BigIntegerField(u'Entrez ID', blank=False)
#     refseq_id = models.CharField(u'RefSeq ID', max_length=REFSEQ_ID_MAX_LENGTH, null=True, blank=True)
#     symbol_id = models.CharField(u'Symbol ID', max_length=SYMBOL_ID_MAX_LENGTH, null=True, blank=True)
#
#     class Meta:
#         verbose_name = 'id map'
#         verbose_name_plural = 'id maps'
#         db_table = 'id_map'
#         unique_together = (('species', 'refseq_id', 'symbol_id'),)
#
#     def __unicode__(self):
#         return u'{}(entrez={}, refseq={}, symbol={})'.format(
#             self.species, self.entrez_id, self.refseq_id or 'None', self.symbol_id or 'None')