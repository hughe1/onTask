from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from jobs.models import Profile, User, Task, ProfileTask
from jobs.serializers import TaskGetSerializer, TaskPostSerializer

# Return a token to authorise API calls
def api_login(user):
    token, created = Token.objects.get_or_create(user=user)
    return token.key

# Create a user indexed by the argument user_number
def create_user(user_num):
    user = User.objects.create(
        username="test{}_user".format(user_num),
        email="test{}@user.com".format(user_num),
        password="testing1234",
        first_name="test{}".format(user_num),
        last_name="user{}".format(user_num)
    )
    return user  

# Update profile information
def update_profile(user, user_num):
    profile = Profile.objects.get(user=user)
    profile.location = "Location {}".format(user_num)
    profile.description = "Description {}".format(user_num)
    return profile

# Create a user and profile and return the profile
def create_profile(user_num):
    user = create_user(user_num)
    profile = update_profile(user, user_num)
    return profile
    
# Create and return a task
def create_task(owner_prof, task_num):
    task = Task.objects.create(
        title="Task {}".format(task_num),
        description="Desc {}".format(task_num),
        points=0,
        location="Loc {}".format(task_num),
        owner=owner_prof
    )
    return task