# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('searcher', '0002_auto_20151130_1258'),
    ]

    operations = [
        migrations.CreateModel(
            name='Other2Entrez',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('species', models.CharField(max_length=50, verbose_name='Species', choices=[(b'hs', b'Homo Sapiens'), (b'mm', b'Mus Musculus'), (b'rt', b'Rattus Norvegicus')])),
                ('entrez_id', models.BigIntegerField(verbose_name='Entrez ID', db_index=True)),
                ('other_id', models.CharField(max_length=50, verbose_name='Other ID', db_index=True)),
            ],
            options={
                'db_table': 'other_to_entrez',
                'verbose_name': 'other2entrez map',
                'verbose_name_plural': 'other2entrez maps',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='other2entrez',
            unique_together=set([('species', 'other_id', 'entrez_id')]),
        ),
    ]
