# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-07 02:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0027_auto_20170906_1702'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='photo',
            field=models.ImageField(default='PLACEHOLDER.jpg', upload_to=''),
        ),
    ]
