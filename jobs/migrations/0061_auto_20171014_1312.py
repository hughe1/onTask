# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-14 02:12
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0060_auto_20171014_1232'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profileskill',
            name='profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='profile_skills', to='jobs.Profile'),
        ),
    ]
