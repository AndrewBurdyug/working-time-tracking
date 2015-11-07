# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('timesheet', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Salary',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('position', models.CharField(null=True, blank=True, max_length=50)),
                ('hourly_rate', models.FloatField()),
                ('currency', models.CharField(choices=[('USD', 'Dollar'), ('RUB', 'Ruble'), ('EUR', 'Euro')], max_length=3)),
            ],
        ),
        migrations.RemoveField(
            model_name='company',
            name='hourly_rate',
        ),
        migrations.RemoveField(
            model_name='company',
            name='invoice_abbr',
        ),
        migrations.RemoveField(
            model_name='company',
            name='salary_currency',
        ),
        migrations.AddField(
            model_name='spenttime',
            name='worker',
            field=models.ForeignKey(default=1, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='salary',
            name='company',
            field=models.ForeignKey(to='timesheet.Company'),
        ),
        migrations.AddField(
            model_name='salary',
            name='worker',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]
