# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-04 04:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0053_delete_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='shortlists',
            field=models.IntegerField(default=0),
        ),
    ]
