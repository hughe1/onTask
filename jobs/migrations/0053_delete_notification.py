# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-27 03:07
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0052_remove_profileskill_rating'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Notification',
        ),
    ]