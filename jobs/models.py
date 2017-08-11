from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User

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
    

class UserSkill(models.Model):
    skills = models.ForeignKey('jobs.Skill')
    user = models.ForeignKey(User)
    rating = models.FloatField()


# TODO - discuss whether this needs to be split up in to HelperJob and PosterJob
class UserJob(models.Model):
    OPEN = 'O'
    SHORTLISTED = 'SL'
    ASSIGNED = 'A'
    COMPLETE = 'C'
    STATUS_CHOICES = (
        (OPEN, 'Open'),
        (SHORTLISTED, 'Shortlisted'),
        (ASSIGNED, 'Assigned'),
        (COMPLETE, 'Complete')
    )
    status = models.CharField(
        max_length=2,
        choices=STATUS_CHOICES,
        default=OPEN
    )
    task = models.ForeignKey('jobs.Task')
    user = models.ForeignKey(User)
    

class Comment(models.Model):
    user = models.ForeignKey(User)
    task = models.ForeignKey('jobs.Task')
    text = models.TextField(max_length=1000)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=128) # could update to choices
    description = models.TextField(max_length=2000)
    photo = models.ImageField(blank=True)
    
    def get_points():
        pass
        
    def get_rating():
        pass
    

# TODO work out how we handle notifications
class Notification(models.Model):
    pass
