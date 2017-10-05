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
        self.assertEqual(response.data['username'], 'test_user')
        self.assertEqual(response.data['first_name'], 'test')
        self.assertEqual(response.data['last_name'], 'user')


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
            offer=0,
            location="Location 1",
            owner=self.profile1
        )
        # Create a task with a helper
        self.task2 = Task.objects.create(
            title="Test Task 2",
            description="Description 2",
            offer=20,
            location="Location 2",
            owner=self.profile2,
            helper=self.profile1
        )
        
    def test_task_list(self):
        """
        Test whether the right list of tasks is returned
        ID: UT02.01
        """
        token = api_login(self.user1)
        url = reverse('task-list')
        response = self.client.get(url, format='json', HTTP_AUTHORIZATION='Token {}'.format(token))
        tasks = Task.objects.all()
        serializer = TaskGetSerializer(tasks, many=True)
        self.assertEqual(len(response.data), len(serializer.data))


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
                  'offer' : 50,
                  'location' : 'Loc 1',
                  'is_remote' : True,
                  'skills': [self.skill1.code, self.skill2.code]
                }
        response = self.client.post(url, data, format="json", HTTP_AUTHORIZATION='Token {}'.format(token))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Task 1")
        self.assertEqual(response.data["description"], "Desc 1")
        self.assertEqual(response.data["offer"], 50)
        self.assertEqual(response.data["location"], "Loc 1")
        self.assertEqual(len(response.data["skills"]), 2)
        
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
        data = {'task': self.task2.id}
        response = self.client.post(url, data, format="json", HTTP_AUTHORIZATION='Token {}'.format(token))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
    # Ensure a user cannot shortlist a task they have already shortlisted    
    def test_shortlist_already_shortlisted(self):
        """
        ID: UT04.02
        """
        token = api_login(self.profile1.user)
        url = reverse('task-shortlist')
        data = {'task': self.task2.id}
        response1 = self.client.post(url, data, format="json", HTTP_AUTHORIZATION='Token {}'.format(token))
        response2 = self.client.post(url, data, format="json", HTTP_AUTHORIZATION='Token {}'.format(token))

        # First response should be success, second failure
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)


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
        url = reverse('task-apply', kwargs={'task_id': self.task1.id})

        data = {
          "profiletask_id" : "1",
          "answer1" : "ans1",
          "answer2" : "ans2",
          "answer3" : "ans3"
        }
        response = self.client.post(url, data, format="json", HTTP_AUTHORIZATION='Token {}'.format(token))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
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

        url = reverse('task-apply', kwargs={'task_id': self.task1.id})
        self.profile_task1 = ProfileTask.objects.filter(profile=self.profile1, task=self.task1)[0]

        data = {
          "profiletask_id" : self.profile_task1.id,
          "answer1" : "ans1",
          "answer2" : "ans2",
          "answer3" : "ans3"
        }
        response = self.client.post(url, data, format="json", HTTP_AUTHORIZATION='Token {}'.format(token))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_apply_shortlisted(self):
        """
        ID: UT06.03
        """
        #shortlist the task
        token = api_login(self.profile1.user)
        url = reverse('task-shortlist')
        data = {'task': self.task2.id}
        response = self.client.post(url, data, format="json", HTTP_AUTHORIZATION='Token {}'.format(token))

        url = reverse('task-apply', kwargs={'task_id': self.task2.id})
        self.profile_task1 = ProfileTask.objects.get(profile=self.profile1, task=self.task2)

        data = {
          "profiletask_id" : self.profile_task1.id,
          "answer1" : "ans1",
          "answer2" : "ans2",
          "answer3" : "ans3"
        }
        # first apply - should pass
        response = self.client.post(url, data, format="json", HTTP_AUTHORIZATION='Token {}'.format(token))
        # Shortlisting a task creates a ProfileTask hence the 201 Status code
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        #attempt to reapply - should fail
        response = self.client.post(url, data, format="json", HTTP_AUTHORIZATION='Token {}'.format(token))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        


