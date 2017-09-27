"""job_bilby Definition of database models in the Jobs application

This file belongs to the back end source code for team 'job-bilby' for the
University of Melbourne subject SWEN90014 Masters Software Engineering Project.
The project is a mobile-first web application for sharing tasks.
The back-end is based on the REST Framework for Django.

Client: Paul Ashkar (Capgemini)                 paul.ashkar@capgemini.com
Supervisor: Rachel Burrows                      rachel.burrows@unimelb.edu.au
Team:
Annie Zhou:                                     azhou@student.unimelb.edu.au
David Barrel:                                   dbarrell@student.unimelb.edu.au
Grace Johnson:                                  gjohnson1@student.unimelb.edu.au
Hugh Edwards:                                   hughe@student.unimelb.edu.au
Matt Perrot:                                    mperrott@student.unimelb.edu.au 
View our 'Project Overview' document on Confluence for more information about the project.
Date project started: 6/8/2017
Date project completed: 15/10/2017
"""
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

class BaseModel(models.Model):
    """ The base model provides basic attributes that all models inherit """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    enabled = models.BooleanField(default=True, verbose_name='active')

    class Meta:
        """ Provides a default ordering for the BaseModel """
        abstract = True
        ordering = ['-created_at']

    @property
    def time_since_create(self):
        """Return time since the model was created  """
        return timesince(self.created_at).split(',')[0]


class Profile(BaseModel):
    """ Model for a Profile
        Each Profile is related to one and only one User.
        Profile essentially adds extra functionality on top of the User model
        provided by Django.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=128, blank=True) # could update to choices
    description = models.TextField(max_length=2000, blank=True)
    photo = models.ImageField(upload_to='%Y/%m/%d/', blank=True, null=True)
    rating = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)



    def __str__(self):
        return self.user.username

    def get_points():
        pass

    def get_rating():
        pass

class Task(BaseModel):
    """ Model for a Task """

    # Enumeration of possible statuses
    OPEN = 'O'
    IN_PROGRESS = 'I'
    COMPLETE = 'C'
    STATUS_CHOICES = (
        (OPEN, 'Open'),
        (IN_PROGRESS, 'In Progress'),
        (COMPLETE, 'Complete')
    )
    status = models.CharField(
        max_length=2,
        choices = STATUS_CHOICES,
        default=OPEN
    )

    title = models.CharField(max_length=128)
    description = models.TextField(max_length=2000)
    points = models.IntegerField()
    location = models.CharField(max_length=128)

    # Specification of whether the task can be completed from a remote location
    is_remote = models.BooleanField(default=False)

    # Profile that posted the Task (Poster)
    owner = models.ForeignKey('jobs.Profile',related_name="poster")

    # Profile that has been accepted for the Task (Helper).
    # Null if no Profile has been accepted for the Task.
    helper = models.ForeignKey('jobs.Profile',related_name="helper",blank=True,null=True)

    # Three questions, to be answered by applicants for the Task
    # Questions are set by the Poster.
    question1 = models.CharField(max_length=300,blank=True)
    question2 = models.CharField(max_length=300,blank=True)
    question3 = models.CharField(max_length=300,blank=True)
    
    skills = models.ManyToManyField('jobs.Skill')

    # display_rank is a blank field which is used as a placeholder
    # for a temporary value used in serializing.
    # Allows a temporary rank value to be used, without concurrency
    # issues (the rank is never written or read from the database)
    display_rank = models.IntegerField(blank=True,null=True)

    def __str__(self):
        return self.title


class Skill(BaseModel):
    """ Model for a Skill
        Skills are created by site administrators.
        They may be selected as required for Tasks by the Poster
        They may also be listed as proficiencies on Profiles.
     """
    title = models.CharField(max_length=128)
    image = models.ImageField(blank=True)
    code = models.CharField(max_length=20)

    def __str__(self):
        return self.title


class ProfileSkill(BaseModel):
    """ Associative Entity between Profiles and Skills
        Manually created (instead of using Django default many-to-many
        So that profiles could have ratings for each skill, potentially
        in future builds.
    """
    skill = models.ForeignKey('jobs.Skill')
    profile = models.ForeignKey('jobs.Profile')

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
