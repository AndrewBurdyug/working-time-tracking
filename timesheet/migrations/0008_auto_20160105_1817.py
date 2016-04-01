# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('timesheet', '0007_auto_20160105_1806'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bonus',
            name='company',
            field=models.ForeignKey(to='timesheet.Company', related_name='bonuses'),
        ),
    ]
