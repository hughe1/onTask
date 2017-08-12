from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


# TODO add datetimes (date joined, date commented, etc)

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
    user = models.ForeignKey(User)
    date_posted = models.DateTimeField(auto_now=True)
    
    # TODO question1, question2 etc - might be better with a many-to-many field
    # instead of hard-code attributes
    status = models.CharField(
        max_length=2,
        choices = STATUS_CHOICES,
        default=INCOMPLETE
    )
    
    def __str__(self):
        return self.title
    

class Skill(models.Model):
    title = models.CharField(max_length=128)
    description = models.TextField(max_length=2000)
    image = models.ImageField(blank=True)

    def __str__(self):
        return self.title
    

class UserSkill(models.Model):
    skills = models.ForeignKey('jobs.Skill')
    user = models.ForeignKey(User)
    rating = models.FloatField()

    def __str__(self):
        return "UserSkill: "+self.skills.title +" ("+ self.user.username + ")"


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

    def __str__(self):
        return "UserJob: "+self.task.title +" ("+ self.user.username + ")"
    

class Comment(models.Model):
    user = models.ForeignKey(User)
    task = models.ForeignKey('jobs.Task')
    text = models.TextField(max_length=1000)
    date_posted = models.DateTimeField(auto_now=True)


    def __str__(self):
        return "Comment: "+self.task.title +" ("+ self.user.username + ")"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=128, blank=True) # could update to choices
    description = models.TextField(max_length=2000, blank=True)
    photo = models.ImageField(blank=True)
    date_created = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.user.username
    
    def get_points():
        pass
        
    def get_rating():
        pass

# Ensures that a Profile instance is created each time a User is created   
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

# Ensures that the Profile is saved when a User is saved
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

# TODO work out how we handle notifications
class Notification(models.Model):
    pass
