# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-15 00:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0038_merge_20170913_1832'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profiletask',
            name='status',
            field=models.CharField(choices=[('SL', 'Shortlisted'), ('AS', 'Assigned'), ('AP', 'Applied'), ('D', 'Discarded'), ('R', 'Rejected'), ('ASL', 'Application Shortlisted')], default='SL', max_length=3),
        ),
    ]
