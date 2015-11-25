# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import djorm_pgarray.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GQModule',
            fields=[
                ('species', models.CharField(max_length=50, verbose_name='Species', choices=[(b'hs', b'Homo Sapiens'), (b'mm', b'Mus Musculus'), (b'rt', b'Rattus Norvegicus')])),
                ('full_name', models.CharField(help_text='Module name specified as &lt;series name&gt;_&lt;platform name&gt;#&lt;module number&gt;', max_length=50, serialize=False, verbose_name='Module', primary_key=True)),
                ('entrez_ids', djorm_pgarray.fields.IntegerArrayField(help_text='Entrez IDs of genes contained in this module. Should be separated by comma.', verbose_name=b'Entrez IDs', blank=False)),
            ],
            options={
                'db_table': 'modules',
                'verbose_name': 'Module',
                'verbose_name_plural': 'Modules',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='IdMap',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('species', models.CharField(max_length=50, verbose_name='Species', choices=[(b'hs', b'Homo Sapiens'), (b'mm', b'Mus Musculus'), (b'rt', b'Rattus Norvegicus')])),
                ('entrez_id', models.BigIntegerField(verbose_name='Entrez ID')),
                ('refseq_id', models.CharField(max_length=50, null=True, verbose_name='RefSeq ID', blank=True)),
                ('symbol_id', models.CharField(max_length=50, null=True, verbose_name='Symbol ID', blank=True)),
            ],
            options={
                'db_table': 'id_map',
                'verbose_name': 'id map',
                'verbose_name_plural': 'id maps',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ModuleDescription',
            fields=[
                ('series', models.CharField(max_length=50, serialize=False, verbose_name='Series ID', primary_key=True)),
                ('title', models.TextField(null=True)),
            ],
            options={
                'db_table': 'module_descriptions',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='idmap',
            unique_together=set([('species', 'refseq_id', 'symbol_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='gqmodule',
            unique_together=set([('species', 'full_name')]),
        ),
    ]
