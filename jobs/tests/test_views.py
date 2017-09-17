from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from jobs.models import Profile, User, Task, ProfileTask
from jobs.serializers import TaskGetSerializer, TaskPostSerializer
from jobs.tests.test_helper import *

"""
Note: The coding style followed for these unit tests is deliberately very
verbose. It does not follow a DRY coding style, but a DAMP coding style
to increase the readability of tests. There is minimal risk associated with
repeated code as each test is isolated. This also allows small tweaks to be
made to tests that are similar but not exactly the same.
https://stackoverflow.com/questions/6453235/what-does-damp-not-dry-mean-when-talking-about-unit-tests
"""


class ProfileTests(APITestCase):
    
    def test_create_profile(self):
        """
        Ensure we can create a new Profile (and subsequently, User)
        ID: UT01.01
        """
        url = reverse('profile-create')
        data = {
                  'username' : 'test_user',
                  'email' : 'test@user.com',
                  'first_name' : 'test',
                  'last_name' : 'user',
                  'password': 'testing1234',
                  'location' : 'TestVille',
                  'description' : 'This is a test description.'
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
        self.user1 = create_user(1)
        self.user2 = create_user(2)
        # Update profile info
        self.profile1 = update_profile(self.user1, 1)
        self.profile2 = update_profile(self.user2, 2)
        
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
    def test_task_list(self):
        """
        Test whether the right list of tasks is returned
        ID: UT02.01
        """
        url = reverse('profile-list')
        response = self.client.get(url, format='json')
        tasks = Task.objects.all()
        serializer = TaskPostSerializer(tasks, many=True)
        print("Response.data: ")
        print(response.data)
        print("")
        print("Serializer.data ")
        print(serializer.data)
        print("")
        self.assertEqual(response.data, serializer.data)


class TestTaskCreate(APITestCase):
    
    def setUp(self):  
        self.user1 = create_user(1)
        self.skill1 = create_skill("Python")
        self.skill2 = create_skill("PHP")
    
    # Test that a task can be created
    def test_task_create(self):
        """
        ID: UT03.01
        """
        token = api_login(self.user1)
        url = reverse('task-create')
        data = {
                  'title' : 'Task 1',
                  'description' : 'Desc 1',
                  'points' : 50,
                  'location' : 'Loc 1',
                  'is_remote' : True,
                  'skills': [self.skill1.code, self.skill2.code]
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
        """
        ID: UT04.01
        """
        token = api_login(self.profile1.user)
        url = reverse('task-shortlist')
        data = {'task': self.task1.id}
        response = self.client.post(url, data, format="json", HTTP_AUTHORIZATION='Token {}'.format(token))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ProfileTask.objects.count(), 1)
        
    # Ensure a user cannot shortlist a task they have already shortlisted    
    def test_shortlist_already_shortlisted(self):
        """
        ID: UT04.02
        """
        token = api_login(self.profile1.user)
        url = reverse('task-shortlist')
        data = {'task': self.task1.id}
        response1 = self.client.post(url, data, format="json", HTTP_AUTHORIZATION='Token {}'.format(token))
        response2 = self.client.post(url, data, format="json", HTTP_AUTHORIZATION='Token {}'.format(token))

        #first response should be success, second failure
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)

        self.assertEqual(ProfileTask.objects.count(), 1)



class TestDiscardTask(APITestCase):
    
    def setUp(self):
        self.profile1 = create_profile(1)
        self.task1 = create_task(self.profile1, 1)
        self.profile2 = create_profile(2)
        self.task2 = create_task(self.profile2, 2)
        
    # Ensure a user can discard a task they have not already discarded
    def test_discard_not_already_discarded(self):
        """
        ID: UT05.01
        """
        token = api_login(self.profile1.user)
        url = reverse('task-discard')
        data = {'task': self.task1.id}
        response = self.client.post(url, data, format="json", HTTP_AUTHORIZATION='Token {}'.format(token))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ProfileTask.objects.count(), 1)
        
    # Ensure a user cannot discard a task they have already discarded    
    def test_discard_already_discarded(self):
        """
        ID: UT05.02
        """
        token = api_login(self.profile1.user)
        url = reverse('task-discard')
        data = {'task': self.task1.id}
        response1 = self.client.post(url, data, format="json", HTTP_AUTHORIZATION='Token {}'.format(token))
        response2 = self.client.post(url, data, format="json", HTTP_AUTHORIZATION='Token {}'.format(token))

        #first response should be success, second failure
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)

        self.assertEqual(ProfileTask.objects.count(), 1)
        #pass        
        
        
class TestApplyTask(APITestCase):
    
    def setUp(self):
        self.profile1 = create_profile(1)
        self.task1 = create_task(self.profile1, 1)
        self.profile2 = create_profile(2)
        self.task2 = create_task(self.profile2, 2)

    # User should not be able to apply for an unshortlisted task
    def test_apply_unshortlisted(self):
        """
        ID: UT06.01
        """
        token = api_login(self.profile1.user)
        url = reverse('task-apply')

        data = {
          "profiletask_id" : "1",
          "answer1" : "ans1",
          "answer2" : "ans2",
          "answer3" : "ans3"
        }
        response = self.client.post(url, data, format="json", HTTP_AUTHORIZATION='Token {}'.format(token))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(ProfileTask.objects.count(), 0)
        
    # Ensure a user can apply to a task they have not already applied for
    def test_apply_discarded(self):
        """
        ID: UT06.02
        """
        #discard the task
        token = api_login(self.profile1.user)
        url = reverse('task-discard')
        data = {'task': self.task1.id}
        response = self.client.post(url, data, format="json", HTTP_AUTHORIZATION='Token {}'.format(token))

        url = reverse('task-apply')
        self.profile_task1 = ProfileTask.objects.filter(profile=self.profile1, task=self.task1)[0]

        data = {
          "profiletask_id" : self.profile_task1.id,
          "answer1" : "ans1",
          "answer2" : "ans2",
          "answer3" : "ans3"
        }
        response = self.client.post(url, data, format="json", HTTP_AUTHORIZATION='Token {}'.format(token))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(ProfileTask.objects.count(), 1)

    def test_apply_shortlisted(self):
        """
        ID: UT06.03
        """
        #shortlist the task
        token = api_login(self.profile1.user)
        url = reverse('task-shortlist')
        data = {'task': self.task1.id}
        response = self.client.post(url, data, format="json", HTTP_AUTHORIZATION='Token {}'.format(token))

        url = reverse('task-apply')
        self.profile_task1 = ProfileTask.objects.filter(profile=self.profile1, task=self.task1)[0]

        data = {
          "profiletask_id" : self.profile_task1.id,
          "answer1" : "ans1",
          "answer2" : "ans2",
          "answer3" : "ans3"
        }
        # first apply - should pass
        response = self.client.post(url, data, format="json", HTTP_AUTHORIZATION='Token {}'.format(token))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        #attempt to reapply - should fail
        response = self.client.post(url, data, format="json", HTTP_AUTHORIZATION='Token {}'.format(token))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(ProfileTask.objects.count(), 1)
        


