from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

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
    photo = models.ImageField(upload_to='%Y/%m/%d/', blank=True, null=True)



    def __str__(self):
        return self.user.username

    def get_points():
        pass

    def get_rating():
        pass


# TODO - default photo
class Task(BaseModel):
    OPEN = 'O'
    IN_PROGRESS = 'I'
    COMPLETE = 'C'
    STATUS_CHOICES = (
        (OPEN, 'Open'),
        (IN_PROGRESS, 'In Progress'),
        (COMPLETE, 'Complete')
    )
    title = models.CharField(max_length=128)
    description = models.TextField(max_length=2000)
    points = models.IntegerField()
    location = models.CharField(max_length=128)
    is_remote = models.BooleanField(default=False)
    owner = models.ForeignKey('jobs.Profile',related_name="poster")
    helper = models.ForeignKey('jobs.Profile',related_name="helper",blank=True,null=True)
    # TODO question1, question2 etc - might be better with a many-to-many field
    # instead of hard-code attributes
    question1 = models.CharField(max_length=300,blank=True)
    question2 = models.CharField(max_length=300,blank=True)
    question3 = models.CharField(max_length=300,blank=True)
    status = models.CharField(
        max_length=2,
        choices = STATUS_CHOICES,
        default=OPEN
    )
    skills = models.ManyToManyField('jobs.Skill')

    # display_rank is a blank field which is only filled in (and note saved) when serialized
    # task is returned. Basically allows a temporary rank value to be inserted, without concurrency
    # issues (the rank is never read from the database; only filled in in memory when it is being
    # returned )
    display_rank = models.IntegerField(blank=True,null=True)

    def __str__(self):
        return self.title


class Skill(BaseModel):
    title = models.CharField(max_length=128)
    image = models.ImageField(blank=True)
    code = models.CharField(max_length=20)

    def __str__(self):
        return self.title


class ProfileSkill(BaseModel):
    skill = models.ForeignKey('jobs.Skill')
    profile = models.ForeignKey('jobs.Profile')
    # TODO - Potentially implement rating for Sprint 3
    rating = models.FloatField(null=True, blank=True)

    def __str__(self):
        return "ProfileSkill: "+self.skill.title +" ("+ self.profile.user.username + ")"


class ProfileTask(BaseModel):
    task = models.ForeignKey('jobs.Task')
    profile = models.ForeignKey('jobs.Profile')
    SHORTLISTED = 'SL'
    APPLIED = 'AP'
    ASSIGNED = 'AS'
    DISCARDED = 'D'
    REJECTED = 'R'
    APPLICATION_SHORTLISTED = 'ASL'
    STATUS_CHOICES = (
        (SHORTLISTED, 'Shortlisted'),
        (ASSIGNED, 'Assigned'),
        (APPLIED, 'Applied'),
        (DISCARDED, 'Discarded'),
        (REJECTED, 'Rejected'),
        (APPLICATION_SHORTLISTED, 'Application Shortlisted')

    )
    status = models.CharField(
        max_length=3,
        choices=STATUS_CHOICES,
        default=SHORTLISTED
    )
    answer1 = models.CharField(max_length=300,blank=True)
    answer2 = models.CharField(max_length=300,blank=True)
    answer3 = models.CharField(max_length=300,blank=True)
    quote = models.IntegerField(blank=True,null=True)
    rating = models.IntegerField(blank=True, null=True)


    def __str__(self):
        return "ProfileTask: "+self.task.title +" ("+ self.profile.user.username + ")"


class Comment(BaseModel):
    profile = models.ForeignKey('jobs.Profile')
    task = models.ForeignKey('jobs.Task')
    text = models.TextField(max_length=1000)

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
