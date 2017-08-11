from __future__ import unicode_literals
from django.db import models

class Task(models.Model):
    INCOMPLETE = 'IC'
    COMPLETE = 'C'
    STATUS_CHOICES = (
        (INCOMPLETE, 'Incomplete'),
        (COMPLETE, 'Complete')
    )
    title = models.CharField(max_length=128)
    description = models.TextField(max_length=2000)
    points = models.IntegerField()
    location = models.CharField(max_length=128)
    isRemote = models.BooleanField
    # TODO question1, question2 etc - might be better with a many-to-many field
    # instead of hard-code attributes
    status = models.CharField(
        max_length=2,
        choices = STATUS_CHOICES,
        default=INCOMPLETE
    )
    
class Skill(models.Model):
    title = models.CharField(max_length=128)
    description = models.TextField(max_length=2000)
    image = models.ImageField(blank=True)
