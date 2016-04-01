# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import timesheet.utils.datetime_helpers


class Migration(migrations.Migration):

    dependencies = [
        ('timesheet', '0006_bonus'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='bonus',
            options={'verbose_name': 'bonus', 'verbose_name_plural': 'bonuses'},
        ),
        migrations.AddField(
            model_name='monthlyinvoice',
            name='timestamp',
            field=models.DateTimeField(help_text='invoice timestamp', default=timesheet.utils.datetime_helpers.current_datetime),
        ),
    ]
