# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('timesheet', '0002_auto_20151107_2202'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='salary',
            options={'verbose_name': 'salary', 'verbose_name_plural': 'salaries'},
        ),
    ]
