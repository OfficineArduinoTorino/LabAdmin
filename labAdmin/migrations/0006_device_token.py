# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-18 14:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('labAdmin', '0005_auto_20161012_1223'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='token',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
    ]
