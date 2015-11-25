# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('searcher', '0002_auto_20151125_1040'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='modulegenes',
            table='modules',
        ),
    ]
