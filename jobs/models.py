from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    enabled = models.BooleanField(default=True, verbose_name='active')

    class Meta:
        abstract = True
        ordering = ['-created_at']

    @property
    def time_since_create(self):
        return timesince(self.created_at).split(',')[0]

class Profile(BaseModel):
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


class Task(BaseModel):
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
    is_remote = models.BooleanField
    user = models.ForeignKey(Profile)
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


class Skill(BaseModel):
    title = models.CharField(max_length=128)
    description = models.TextField(max_length=2000)
    image = models.ImageField(blank=True)

    def __str__(self):
        return self.title


class UserSkill(BaseModel):
    skills = models.ForeignKey('jobs.Skill')
    user = models.ForeignKey(Profile)
    rating = models.FloatField()

    def __str__(self):
        return "UserSkill: "+self.skills.title +" ("+ self.user.username + ")"


# TODO - discuss whether this needs to be split up in to HelperJob and PosterJob
class UserJob(BaseModel):
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
    user = models.ForeignKey(Profile)

    def __str__(self):
        return "UserJob: "+self.task.title +" ("+ self.user.username + ")"


class Comment(BaseModel):
    user = models.ForeignKey(Profile)
    task = models.ForeignKey('jobs.Task')
    text = models.TextField(max_length=1000)
    date_posted = models.DateTimeField(auto_now=True)


    def __str__(self):
        return "Comment: "+self.task.title +" ("+ self.user.username + ")"


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
class Notification(BaseModel):
    pass
