# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-17 00:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0039_auto_20170915_1055'),
    ]

    operations = [
        migrations.AddField(
            model_name='profiletask',
            name='rating',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]