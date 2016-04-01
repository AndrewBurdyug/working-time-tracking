# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import timesheet.utils.datetime_helpers
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('timesheet', '0005_auto_20151108_2218'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bonus',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('amount', models.FloatField()),
                ('currency', models.CharField(choices=[('USD', 'Dollar'), ('RUB', 'Ruble'), ('EUR', 'Euro')], max_length=3)),
                ('date', models.DateTimeField(default=timesheet.utils.datetime_helpers.current_datetime, help_text='bonus date')),
                ('company', models.ForeignKey(to='timesheet.Company')),
                ('worker', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
