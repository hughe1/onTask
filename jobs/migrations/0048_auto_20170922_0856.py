# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-21 22:56
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0047_remove_skill_description'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='profile',
        ),
        migrations.RemoveField(
            model_name='comment',
            name='task',
        ),
        migrations.DeleteModel(
            name='Comment',
        ),
    ]
