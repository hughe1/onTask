# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-27 02:57
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0051_auto_20170926_0935'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profileskill',
            name='rating',
        ),
    ]
