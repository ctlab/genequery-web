# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('searcher', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='modulegenes',
            old_name='module',
            new_name='full_name',
        ),
        migrations.RemoveField(
            model_name='moduledescription',
            name='experiment_type',
        ),
        migrations.RemoveField(
            model_name='moduledescription',
            name='organisms',
        ),
        migrations.RemoveField(
            model_name='moduledescription',
            name='overall_design',
        ),
        migrations.RemoveField(
            model_name='moduledescription',
            name='status',
        ),
        migrations.RemoveField(
            model_name='moduledescription',
            name='summary',
        ),
        migrations.AlterField(
            model_name='idmap',
            name='species',
            field=models.CharField(max_length=50, verbose_name='Species', choices=[(b'hs', b'Homo Sapiens'), (b'mm', b'Mus Musculus')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='modulegenes',
            name='species',
            field=models.CharField(max_length=50, verbose_name='Species', choices=[(b'hs', b'Homo Sapiens'), (b'mm', b'Mus Musculus')]),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='modulegenes',
            unique_together=set([('species', 'full_name')]),
        ),
    ]
