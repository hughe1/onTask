# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-12 06:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0013_auto_20170812_0606'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='date_posted',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='date_created',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
