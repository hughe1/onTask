# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-21 00:21
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0045_auto_20170918_1407'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='photo',
        ),
    ]
