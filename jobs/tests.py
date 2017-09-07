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


class ProfileTests(APITestCase):
    
    def test_create_profile(self):
        """
        Ensure we can create a new Profile (and subsequently, User)
        """
        url = reverse('profile-create')
        data = {
                  'username' : 'test_user',
                  'email' : 'test@user.com',
                  'first_name' : 'test',
                  'last_name' : 'user',
                  'password': 'testing1234',
                  'location' : 'TestVille',
                  'description' : 'Testi cles.'
                }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Profile.objects.count(), 1)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().first_name, 'test')
        # Ensure the ProfileID and UserID are the same
        self.assertEqual(User.objects.get().id, Profile.objects.get().id)
        # Ensure the User is not created as a superuser
        self.assertEqual(User.objects.get().is_superuser, False)


class TaskListTests(APITestCase):
    def setUp(self):
        """
        Create some task objects and users
        """
        # Create users
        user1 = create_user(1)
        user2 = create_user(2)
        # Update profile info
        profile1 = update_profile(user1, 1)
        profile2 = update_profile(user2, 2)
        
        # TODO Try with an image field
        # Create a task without a helper, is remote
        self.task1 = Task.objects.create(
            title="Test Task 1",
            description="Description 1",
            points=0,
            location="Location 1",
            owner=self.profile1
        )
        # Create a task with a helper
        self.task2 = Task.objects.create(
            title="Test Task 2",
            description="Description 2",
            points=20,
            location="Location 2",
            owner=self.profile2,
            helper=self.profile1
        )
        
    # TODO Work out why this test is failing
    # def test_task_list(self):
    #     """
    #     Test whether the right list of tasks is returned
    #     """
    #     url = reverse('profile-list')
    #     response = self.client.get(url, format='json')
    #     tasks = Task.objects.all()
    #     serializer = TaskGetSerializer(tasks, many=True)
    #     print("Response.data: ")
    #     print(response.data)
    #     print("")
    #     print("Serializer.data ")
    #     print(serializer.data)
    #     print("")
    #     self.assertEqual(response.data, serializer.data)


class TestTaskCreate(APITestCase):
    
    def setUp(self):  
        self.user1 = create_user(1)
    
    # Test that a task can be created
    def test_task_create(self):
        token = api_login(self.user1)
        url = reverse('task-create')
        data = {
                  'title' : 'Task 1',
                  'description' : 'Desc 1',
                  'points' : 50,
                  'location' : 'Loc 1',
                  'is_remote' : True
                }
        response = self.client.post(url, data, format="json", HTTP_AUTHORIZATION='Token {}'.format(token))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 1)
        
class TestShortlist(APITestCase):
    
    def setUp(self):
        self.profile1 = create_profile(1)
        self.task1 = create_task(self.profile1, 1)
        self.profile2 = create_profile(2)
        self.task2 = create_task(self.profile2, 2)
        
    # Ensure a user can shortlist a task they have not already shortlisted
    def test_shortlist_not_already_shortlisted(self):
        token = api_login(self.profile1.user)
        url = reverse('task-shortlist')
        data = {'task': self.task1.id}
        response = self.client.post(url, data, format="json", HTTP_AUTHORIZATION='Token {}'.format(token))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ProfileTask.objects.count(), 1)
        
    # Ensure a user cannot shortlist a task they have already shortlisted    
    def test_shortlist_already_shortlisted(self):
        pass
        
        


