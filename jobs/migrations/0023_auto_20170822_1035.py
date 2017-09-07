# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-22 00:35
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0022_task_photo'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProfileSkill',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('enabled', models.BooleanField(default=True, verbose_name='active')),
                ('rating', models.FloatField()),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jobs.Profile')),
                ('skill', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jobs.Skill')),
            ],
            options={
                'ordering': ['-created_at'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProfileTask',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('enabled', models.BooleanField(default=True, verbose_name='active')),
                ('status', models.CharField(choices=[('SL', 'Shortlisted'), ('AP', 'Applied'), ('AS', 'Assigned'), ('C', 'Complete'), ('D', 'Discarded'), ('R', 'Rejected')], default='SL', max_length=2)),
                ('answer1', models.CharField(blank=True, max_length=300)),
                ('answer2', models.CharField(blank=True, max_length=300)),
                ('answer3', models.CharField(blank=True, max_length=300)),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jobs.Profile')),
            ],
            options={
                'ordering': ['-created_at'],
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='userskill',
            name='skills',
        ),
        migrations.RemoveField(
            model_name='userskill',
            name='user',
        ),
        migrations.RemoveField(
            model_name='usertask',
            name='profile',
        ),
        migrations.RemoveField(
            model_name='usertask',
            name='task',
        ),
        migrations.RenameField(
            model_name='comment',
            old_name='user',
            new_name='profile',
        ),
        migrations.AddField(
            model_name='task',
            name='question1',
            field=models.CharField(blank=True, max_length=300),
        ),
        migrations.AddField(
            model_name='task',
            name='question2',
            field=models.CharField(blank=True, max_length=300),
        ),
        migrations.AddField(
            model_name='task',
            name='question3',
            field=models.CharField(blank=True, max_length=300),
        ),
        migrations.DeleteModel(
            name='UserSkill',
        ),
        migrations.DeleteModel(
            name='UserTask',
        ),
        migrations.AddField(
            model_name='profiletask',
            name='task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jobs.Task'),
        ),
    ]