# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('timesheet', '0004_auto_20151108_1329'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='abbr',
            field=models.SlugField(help_text='company abbreviation', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='monthlyinvoice',
            name='amount_equivalent',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
