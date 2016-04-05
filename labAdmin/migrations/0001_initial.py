# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-05 13:39
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Devicetype',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Logdevice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bootDevice', models.DateTimeField()),
                ('shutdownDevice', models.DateTimeField()),
                ('startWork', models.DateTimeField()),
                ('finishWork', models.DateTimeField()),
                ('hourlyCost', models.FloatField(default=0.0)),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='labAdmin.Device')),
            ],
        ),
        migrations.CreateModel(
            name='Logdoor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hour', models.DateTimeField()),
                ('doorOpened', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('devicetype', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='labAdmin.Devicetype')),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=200)),
                ('signup', models.DateTimeField()),
                ('subscriptionEnd', models.DateTimeField()),
                ('needSubcription', models.BooleanField(default=True)),
                ('nfcId', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Usertype',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('monday', models.BooleanField(default=False)),
                ('tuesday', models.BooleanField(default=False)),
                ('wednesday', models.BooleanField(default=False)),
                ('thursday', models.BooleanField(default=False)),
                ('friday', models.BooleanField(default=False)),
                ('saturday', models.BooleanField(default=False)),
                ('sunday', models.BooleanField(default=False)),
                ('hourStart', models.TimeField()),
                ('hourEnd', models.TimeField()),
                ('isAdmin', models.BooleanField(default=False)),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='labAdmin.Usertype'),
        ),
        migrations.AddField(
            model_name='logdoor',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='labAdmin.User'),
        ),
        migrations.AddField(
            model_name='logdevice',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='labAdmin.User'),
        ),
        migrations.AddField(
            model_name='device',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='labAdmin.Devicetype'),
        ),
    ]