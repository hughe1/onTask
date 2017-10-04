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
        profile = Profile.objects.get(pk=1)
        user = User.objects.get(pk=1)
        # Check only one profile is created
        self.assertEqual(Profile.objects.count(), 1)
        # Check profile description is correct
        self.assertEqual(profile.description, 'This is a test description.')
        # Check only one user is created
        self.assertEqual(User.objects.count(), 1)
        # Check user details
        self.assertEqual(user.first_name, 'test')
        self.assertEqual(user.last_name, 'user')
        # Ensure the ProfileID and UserID are the same
        self.assertEqual(user.id, profile.id)
        # Ensure the User is not created as a superuser
        self.assertEqual(User.objects.get().is_superuser, False)


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
        task = Task.objects.get(title="Task 1")
        # Check only one task is created
        self.assertEqual(Task.objects.count(), 1)
        # Check task details are correct
        self.assertEqual(task.title, 'Task 1')
        self.assertEqual(task.description, 'Desc 1')
        self.assertEqual(task.points, 50)
        self.assertEqual(task.location, 'Loc 1')
        self.assertEqual(task.is_remote, True)
        self.assertEqual(task.skills.count(), 2)
        self.assertEqual(task.skills.get(code="Py").code, 'Py')
        self.assertEqual(task.skills.get(code="Py").title, 'Python')
        self.assertEqual(task.skills.get(title="PHP").code, 'PH')
        self.assertEqual(task.skills.get(title="PHP").title, 'PHP')


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
        # Get the profile task that is created when a task is shortlisted
        profile_task = ProfileTask.objects.get(profile=self.profile1, task=self.task2)
        # Check profile task details
        self.assertEqual(ProfileTask.objects.count(), 1)
        self.assertEqual(profile_task.task.id, self.task2.id)
        self.assertEqual(profile_task.profile.id, self.profile1.id)
        self.assertEqual(profile_task.status, 'SL')
        
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

        # Get the profile task that is created when a task is shortlisted for the first time
        profile_task = ProfileTask.objects.get(profile=self.profile1, task=self.task2)
        # Check only 1 profile task is created
        self.assertEqual(ProfileTask.objects.count(), 1)
        self.assertEqual(profile_task.task.id, self.task2.id)
        self.assertEqual(profile_task.profile.id, self.profile1.id)
        self.assertEqual(profile_task.status, 'SL')
        

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
        # Get the profile task that is created when a task is discarded
        profile_task = ProfileTask.objects.get(profile=self.profile1, task=self.task1)
        # Check profile task details of discarded task
        self.assertEqual(ProfileTask.objects.count(), 1)
        self.assertEqual(profile_task.status, 'D')
        
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
        # Get the profile task that is created when a task is discarded
        profile_task = ProfileTask.objects.get(profile=self.profile1, task=self.task1)
        # Check profile task details of discarded task
        self.assertEqual(ProfileTask.objects.count(), 1)
        self.assertEqual(profile_task.status, 'D')


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
        # Check no profile task is created
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

        url = reverse('task-apply', kwargs={'task_id': self.task1.id})
        self.profile_task1 = ProfileTask.objects.filter(profile=self.profile1, task=self.task1)[0]

        data = {
          "profiletask_id" : self.profile_task1.id,
          "answer1" : "ans1",
          "answer2" : "ans2",
          "answer3" : "ans3"
        }
        response = self.client.post(url, data, format="json", HTTP_AUTHORIZATION='Token {}'.format(token))
        # Get the discarded profile task
        profile_task = ProfileTask.objects.get(profile=self.profile1, task=self.task1)
        # Check profile task details
        self.assertEqual(ProfileTask.objects.count(), 1)
        self.assertEqual(profile_task.status, 'D')

    def test_apply_shortlisted(self):
        """
        ID: UT06.03
        """
        # Shortlist the task
        token = api_login(self.profile1.user)
        url = reverse('task-shortlist')
        data = {'task': self.task2.id}
        response = self.client.post(url, data, format="json", HTTP_AUTHORIZATION='Token {}'.format(token))

        url = reverse('task-apply', kwargs={'task_id': self.task2.id})
        profile_task = ProfileTask.objects.get(profile=self.profile1, task=self.task2)

        data = {
          "profiletask_id" : profile_task.id,
          "answer1" : "ans1",
          "answer2" : "ans2",
          "answer3" : "ans3"
        }
        # First apply - should pass
        response = self.client.post(url, data, format="json", HTTP_AUTHORIZATION='Token {}'.format(token))
        # Attempt to reapply - should fail
        response = self.client.post(url, data, format="json", HTTP_AUTHORIZATION='Token {}'.format(token))
        # Check only 1 profile task is created
        self.assertEqual(ProfileTask.objects.count(), 1)
        # Get profile task again after it has been applied for
        profile_task = ProfileTask.objects.get(profile=self.profile1, task=self.task2)
        # Check profile task status is APPLIED
        self.assertEqual(profile_task.status, 'AP')
        
class TestShortlistApplication(APITestCase):
    
    def setUp(self):
        self.profile1 = create_profile(1)
        self.profile2 = create_profile(2)
        self.task = create_task(self.profile2, 1)
        self.profile_task = ProfileTask.objects.create(
            profile=self.profile1,
            task=self.task
        )
        self.profile_task.status = ProfileTask.APPLIED
        self.profile_task.save()
        self.task.status = Task.OPEN
        self.task.save()
    
    def test_applicant_shortlist(self):
        token = api_login(self.profile2.user)
        url = reverse('task-shortlist_application')
        data = {'profiletask_id': self.profile_task.id}
        # Shortlist the application
        response = self.client.post(url, data, format="json", HTTP_AUTHORIZATION='Token {}'.format(token))
        # Get the profile task with updated status
        profile_task = ProfileTask.objects.get(task=self.task, profile=self.profile1)
        # Get the profile of the profile task owner
        profile = Profile.objects.get(pk=self.profile1.id)
        # Status of profile task should now be ASL
        self.assertEqual(profile_task.status, ProfileTask.APPLICATION_SHORTLISTED)
        self.assertEqual(profile.shortlists, 1)














        