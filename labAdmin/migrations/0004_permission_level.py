# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-05 17:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('labAdmin', '0003_permission_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='permission',
            name='level',
            field=models.IntegerField(default=0),
        ),
    ]