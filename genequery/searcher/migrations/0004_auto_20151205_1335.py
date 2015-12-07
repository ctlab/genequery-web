# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('searcher', '0003_auto_20151130_1333'),
    ]

    operations = [
        migrations.CreateModel(
            name='Homologene',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('group_id', models.PositiveIntegerField(verbose_name='Group ID', db_index=True)),
                ('species', models.CharField(max_length=50, verbose_name='Species', choices=[(b'hs', b'Homo Sapiens'), (b'mm', b'Mus Musculus'), (b'rt', b'Rattus Norvegicus')])),
                ('entrez_id', models.BigIntegerField(verbose_name='Entrez ID', db_index=True)),
                ('symbol_id', models.CharField(max_length=50, verbose_name='Symbol ID', db_index=True)),
                ('refseq_id', models.CharField(max_length=50, verbose_name='RefSeq ID', db_index=True)),
            ],
            options={
                'db_table': 'homologene',
                'verbose_name': 'homologene',
                'verbose_name_plural': 'homologenes',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='homologene',
            unique_together=set([('group_id', 'species', 'entrez_id', 'symbol_id', 'refseq_id')]),
        ),
    ]
