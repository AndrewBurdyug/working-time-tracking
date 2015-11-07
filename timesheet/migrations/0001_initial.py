# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings
import timesheet.utils.datetime_helpers


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('title', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name_plural': 'Categories',
                'ordering': ['project__company', 'project__title'],
            },
        ),
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('hourly_rate', models.FloatField(blank=True, null=True)),
                ('salary_currency', models.CharField(max_length=3, blank=True, choices=[('USD', 'Dollar'), ('RUB', 'Ruble'), ('EUR', 'Euro')], null=True)),
                ('invoice_abbr', models.CharField(max_length=20, blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'Companies',
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='CompanyInvoiceData',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('address', models.CharField(max_length=120, blank=True, null=True)),
                ('tax_or_vat_id', models.CharField(max_length=20, blank=True, null=True)),
                ('contact_name', models.CharField(max_length=120, blank=True, null=True)),
                ('mention_name', models.CharField(max_length=120, blank=True, null=True)),
                ('phone', models.CharField(max_length=40, blank=True, null=True)),
                ('paypal', models.CharField(max_length=40, blank=True, null=True)),
                ('entity', models.OneToOneField(to='timesheet.Company')),
            ],
            options={
                'verbose_name': 'invoice extra data',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MonthlyInvoice',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('filename', models.FileField(blank=True, null=True, upload_to='invoices')),
                ('year', models.PositiveSmallIntegerField(default=timesheet.utils.datetime_helpers.current_year)),
                ('month', models.PositiveSmallIntegerField(default=timesheet.utils.datetime_helpers.current_month, choices=[(1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'), (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'), (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')])),
                ('currency_equivalent', models.CharField(max_length=3, blank=True, choices=[('USD', 'Dollar'), ('RUB', 'Ruble'), ('EUR', 'Euro')], null=True)),
                ('date', models.DateTimeField(help_text='invoice sending date', default=timesheet.utils.datetime_helpers.current_datetime)),
                ('number', models.PositiveSmallIntegerField(default=1)),
                ('company', models.ForeignKey(to='timesheet.Company')),
                ('worker', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-month', 'company__title'],
            },
        ),
        migrations.CreateModel(
            name='MonthlyReport',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('month', models.PositiveSmallIntegerField(default=timesheet.utils.datetime_helpers.current_month, choices=[(1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'), (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'), (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')])),
                ('year', models.PositiveSmallIntegerField(default=timesheet.utils.datetime_helpers.current_year)),
                ('filename', models.FileField(blank=True, null=True, upload_to='reports')),
            ],
            options={
                'ordering': ['-month', 'project__title'],
            },
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('company', models.ForeignKey(related_name='projects', blank=True, to='timesheet.Company', null=True)),
            ],
            options={
                'ordering': ['company__title', 'title'],
            },
        ),
        migrations.CreateModel(
            name='SpentTime',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField(default=timesheet.utils.datetime_helpers.current_datetime)),
                ('comment', models.CharField(max_length=200)),
                ('duration', models.FloatField(default=0)),
            ],
            options={
                'ordering': ['-end_time'],
            },
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('title', models.CharField(max_length=100)),
                ('status', models.PositiveSmallIntegerField(choices=[(0, 'New'), (1, 'In Progress'), (2, 'Resolved'), (3, 'Feedback'), (4, 'Closed')])),
                ('priority', models.PositiveSmallIntegerField(choices=[(0, 'Low'), (1, 'Normal'), (2, 'Hight'), (3, 'Urgent'), (4, 'Immediate')])),
                ('start_date', models.DateField()),
                ('progress', models.PositiveSmallIntegerField(default=0)),
                ('assigned', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='timesheet.Category', null=True)),
                ('project', models.ForeignKey(related_name='tasks', to='timesheet.Project')),
            ],
            options={
                'ordering': ['project__company', 'project__title', '-title', 'status'],
            },
        ),
        migrations.CreateModel(
            name='UserInvoiceData',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('address', models.CharField(max_length=120, blank=True, null=True)),
                ('tax_or_vat_id', models.CharField(max_length=20, blank=True, null=True)),
                ('contact_name', models.CharField(max_length=120, blank=True, null=True)),
                ('mention_name', models.CharField(max_length=120, blank=True, null=True)),
                ('phone', models.CharField(max_length=40, blank=True, null=True)),
                ('paypal', models.CharField(max_length=40, blank=True, null=True)),
                ('entity', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'invoice extra data',
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='spenttime',
            name='task',
            field=models.ForeignKey(related_name='times', to='timesheet.Task'),
        ),
        migrations.AddField(
            model_name='monthlyreport',
            name='project',
            field=models.ForeignKey(to='timesheet.Project'),
        ),
        migrations.AddField(
            model_name='monthlyreport',
            name='worker',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='category',
            name='project',
            field=models.ForeignKey(related_name='categories', to='timesheet.Project'),
        ),
    ]
