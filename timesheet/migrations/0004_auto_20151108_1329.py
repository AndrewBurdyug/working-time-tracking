# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('timesheet', '0003_auto_20151108_0023'),
    ]

    operations = [
        migrations.AlterField(
            model_name='companyinvoicedata',
            name='entity',
            field=models.OneToOneField(to='timesheet.Company', related_name='iv_data'),
        ),
        migrations.AlterField(
            model_name='userinvoicedata',
            name='entity',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL, related_name='iv_data'),
        ),
    ]
