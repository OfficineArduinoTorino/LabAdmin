# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-27 12:49
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('labadmin', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Card',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nfc_id', models.BigIntegerField(unique=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='logaccess',
            name='user',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='nfcId',
        ),
        migrations.AddField(
            model_name='logaccess',
            name='users',
            field=models.ManyToManyField(to='labadmin.UserProfile'),
        ),
        migrations.AddField(
            model_name='logaccess',
            name='card',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='labadmin.Card'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='userprofile',
            name='card',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='labadmin.Card'),
        ),
    ]
