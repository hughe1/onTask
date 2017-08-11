from __future__ import unicode_literals
from django.db import models

class Task(models.Model):
    title = models.CharField(max_length=128)
    description = models.TextField(max_length=2000)
    points = models.IntegerField()
    location = models.CharField(max_length=128)
    isRemote = models.BooleanField
