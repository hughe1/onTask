# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-12 05:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0008_task_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='date_posted',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
