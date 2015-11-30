# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('searcher', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ensembl2Entrez',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('species', models.CharField(max_length=50, verbose_name='Species', choices=[(b'hs', b'Homo Sapiens'), (b'mm', b'Mus Musculus'), (b'rt', b'Rattus Norvegicus')])),
                ('entrez_id', models.BigIntegerField(verbose_name='Entrez ID')),
                ('ensembl_id', models.CharField(max_length=100, verbose_name='Ensembl ID', db_index=True)),
            ],
            options={
                'db_table': 'ensembl_to_entrez',
                'verbose_name': 'ensembl2entrez map',
                'verbose_name_plural': 'ensembl2entrez maps',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Refseq2Entrez',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('species', models.CharField(max_length=50, verbose_name='Species', choices=[(b'hs', b'Homo Sapiens'), (b'mm', b'Mus Musculus'), (b'rt', b'Rattus Norvegicus')])),
                ('entrez_id', models.BigIntegerField(verbose_name='Entrez ID')),
                ('refseq_id', models.CharField(max_length=50, verbose_name='RefSeq ID', db_index=True)),
            ],
            options={
                'db_table': 'refseq_to_entrez',
                'verbose_name': 'refseq2entrez map',
                'verbose_name_plural': 'refseq2entrez maps',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Symbol2Entrez',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('species', models.CharField(max_length=50, verbose_name='Species', choices=[(b'hs', b'Homo Sapiens'), (b'mm', b'Mus Musculus'), (b'rt', b'Rattus Norvegicus')])),
                ('entrez_id', models.BigIntegerField(verbose_name='Entrez ID', db_index=True)),
                ('symbol_id', models.CharField(max_length=50, verbose_name='Symbol ID', db_index=True)),
            ],
            options={
                'db_table': 'symbol_to_entrez',
                'verbose_name': 'symbol2entrez map',
                'verbose_name_plural': 'symbol2entrez maps',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='symbol2entrez',
            unique_together=set([('species', 'symbol_id', 'entrez_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='refseq2entrez',
            unique_together=set([('species', 'refseq_id', 'entrez_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='ensembl2entrez',
            unique_together=set([('species', 'ensembl_id', 'entrez_id')]),
        ),
    ]
