# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-05-20 19:59
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('labadmin', '0012_auto_20170518_2158'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeviceUserCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=64)),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='labadmin.Device')),
                ('userprofile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='labadmin.UserProfile')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='deviceusercode',
            unique_together=set([('userprofile', 'device', 'code')]),
        ),
    ]
