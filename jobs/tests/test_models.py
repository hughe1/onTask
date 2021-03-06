from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from jobs.models import Profile, User, Task, ProfileTask, ProfileSkill
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
    """ Models tests for creating a profile """    
    
    def test_create_profile(self):
        """
        Ensure we can create a new Profile (and subsequently, User).
        This should successfully create a profile.
        ID: UT-M01.01
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
    """ Model tests for create tasks """
    
    def setUp(self):
        """ Create some users and skills """
        self.user1 = create_user(1)
        self.skill1 = create_skill("Python")
        self.skill2 = create_skill("PHP")
    
    # Test that a task can be created
    def test_task_create(self):
        """ Create a task.
            This should successfully create a task.
            ID: UT-M03.01
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
        task = Task.objects.get(title="Task 1")
        # Check only one task is created
        self.assertEqual(Task.objects.count(), 1)
        # Check task details are correct
        self.assertEqual(task.title, 'Task 1')
        self.assertEqual(task.description, 'Desc 1')
        self.assertEqual(task.offer, 50)
        self.assertEqual(task.location, 'Loc 1')
        self.assertEqual(task.is_remote, True)
        self.assertEqual(task.skills.count(), 2)
        self.assertEqual(task.skills.get(code="Py").code, 'Py')
        self.assertEqual(task.skills.get(code="Py").title, 'Python')
        self.assertEqual(task.skills.get(title="PHP").code, 'PH')
        self.assertEqual(task.skills.get(title="PHP").title, 'PHP')


class TestShortlist(APITestCase):
    """ Model tests for shortlisting a task """
    
    def setUp(self):
        """ Create some profiles and tasks """
        self.profile1 = create_profile(1)
        self.task1 = create_task(self.profile1, 1)
        self.profile2 = create_profile(2)
        self.task2 = create_task(self.profile2, 2)
        
    # Ensure a user can shortlist a task they have not already shortlisted
    def test_shortlist_not_already_shortlisted(self):
        """ Test shortlitisting a task that hasn't already been shortlisted.
            This should successfully create a profile task.
            ID: UT-M04.01
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
        """ Test shortlisting a task that has already been shortlisted.
            There should only be one profile task, not two.
            ID: UT-M04.02
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
    """ Model tests for discarding tasks """
    
    def setUp(self):
        """ Create some profiles and tasks """
        self.profile1 = create_profile(1)
        self.task1 = create_task(self.profile1, 1)
        self.profile2 = create_profile(2)
        self.task2 = create_task(self.profile2, 2)
        
    # Ensure a user can discard a task they have not already discarded
    def test_discard_not_already_discarded(self):
        """ Test discarding a task that hasn't already been discarded.
            This should change the tasks status to discarded.
            ID: UT-M05.01
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
        """ Test discarding a task that has already been discarded.
            This shouldn't create another profile task.
            ID: UT-M05.02
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
    """ Model tests for applying for tasks """
    
    def setUp(self):
        """ Create some tasks and profiles """
        self.profile1 = create_profile(1)
        self.task1 = create_task(self.profile1, 1)
        self.profile2 = create_profile(2)
        self.task2 = create_task(self.profile2, 2)

    def test_apply_unshortlisted(self):
        """ Test applying for a task that isn't shortlisted yet.
            This is allowed.
            ID: UT-M06.01
        """
        token = api_login(self.profile2.user)
        url = reverse('task-apply', kwargs={'task_id': self.task1.id})
        data = {
          "answer1" : "ans1",
          "answer2" : "ans2",
          "answer3" : "ans3"
        }
        self.client.post(url, data, format="json", HTTP_AUTHORIZATION='Token {}'.format(token))
        # Check a profile task is created
        self.assertEqual(ProfileTask.objects.count(), 1)
        
    def test_apply_discarded(self):
        """ Test applying for a task that is already discarded.
            This is not allowed.
            ID: UT-M06.02
        """
        token = api_login(self.profile2.user)
        # Discard the task
        url = reverse('task-discard')
        data = {'task': self.task1.id}
        self.client.post(url, data, format="json", HTTP_AUTHORIZATION='Token {}'.format(token))
        # Apply for the task
        url = reverse('task-apply', kwargs={'task_id': self.task1.id})
        data = {
          "answer1" : "ans1",
          "answer2" : "ans2",
          "answer3" : "ans3"
        }
        self.client.post(url, data, format="json", HTTP_AUTHORIZATION='Token {}'.format(token))
        # Get the discarded profile task
        profile_task = ProfileTask.objects.get(profile=self.profile2, task=self.task1)
        # Check profile task details
        self.assertEqual(ProfileTask.objects.count(), 1)
        self.assertEqual(profile_task.status, 'D')

    def test_apply_shortlisted(self):
        """ Test applying for a task that has been shortlisted.
            This is allowed.
            ID: UT-M06.03
        """
        # Shortlist the task
        token = api_login(self.profile1.user)
        url = reverse('task-shortlist')
        data = {'task': self.task2.id}
        response = self.client.post(url, data, format="json", HTTP_AUTHORIZATION='Token {}'.format(token))
        # Apply for the shortlisted task
        url = reverse('task-apply', kwargs={'task_id': self.task2.id})
        data = {
          "answer1" : "ans1",
          "answer2" : "ans2",
          "answer3" : "ans3"
        }
        # First apply - should pass
        self.client.post(url, data, format="json", HTTP_AUTHORIZATION='Token {}'.format(token))
        # Attempt to reapply - should fail
        self.client.post(url, data, format="json", HTTP_AUTHORIZATION='Token {}'.format(token))
        # Check only 1 profile task is created
        self.assertEqual(ProfileTask.objects.count(), 1)
        # Get profile task again after it has been applied for
        profile_task = ProfileTask.objects.get(profile=self.profile1, task=self.task2)
        # Check profile task status is APPLIED
        self.assertEqual(profile_task.status, 'AP')

    def test_apply_owner(self):
        """ Test applying for a task that is owned.
            This is not allowed.
            ID: UT-M06.04
        """
        token = api_login(self.profile1.user)
        url = reverse('task-apply', kwargs={'task_id': self.task1.id})
        data = {
          "answer1" : "ans1",
          "answer2" : "ans2",
          "answer3" : "ans3"
        }
        response = self.client.post(url, data, format="json", HTTP_AUTHORIZATION='Token {}'.format(token))
        # Check no profile task is created
        self.assertEqual(ProfileTask.objects.count(), 0)

        
class TestShortlistApplication(APITestCase):
    """ Model tests for shortlisting an application """
    
    def setUp(self):
        """ Create some profiles, tasks and profiletasks """
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
        """ Shortlist an applicant.
            This should change profiletask status to APPLICATION_SHORTLISTED.
            ID: UT-M07.01
        """
        token = api_login(self.profile2.user)
        url = reverse('task-shortlist_application')
        data = {'profiletask_id': self.profile_task.id}
        # Shortlist the application
        self.client.post(url, data, format="json", HTTP_AUTHORIZATION='Token {}'.format(token))
        # Get the profile task with updated status
        profile_task = ProfileTask.objects.get(task=self.task, profile=self.profile1)
        # Get the profile of the profile task owner
        profile = Profile.objects.get(pk=self.profile1.id)
        # Status of profile task should now be ASL
        self.assertEqual(profile_task.status, ProfileTask.APPLICATION_SHORTLISTED)
        self.assertEqual(profile.shortlists, 1)
        
    def test_applicant_reject(self):
        """ Reject an applicant.
            This should change profiletask to REJECTED.
            ID: UT-M07.02
        """
        token = api_login(self.profile2.user)
        url = reverse('task-reject_application')
        data = {'profiletask_id': self.profile_task.id}
        # Shortlist the application
        self.client.post(url, data, format="json", HTTP_AUTHORIZATION='Token {}'.format(token))
        # Get the profile task with updated status
        profile_task = ProfileTask.objects.get(task=self.task, profile=self.profile1)
        # Get the profile of the profile task owner
        profile = Profile.objects.get(pk=self.profile1.id)
        # Status of profile task should now be REJECTED
        self.assertEqual(profile_task.status, ProfileTask.REJECTED)


class TestAcceptApplication(APITestCase):
    """ Model tests for accepting an application """
    
    def setUp(self):
        """ Create some profiles, tasks and skills """
        self.profile1 = create_profile(1)
        self.profile2 = create_profile(2)
        self.task = create_task(self.profile2, 1)
        skill = create_skill("Python")
        self.task.skills = [skill]
        self.task.save()
        self.profile_task = ProfileTask.objects.create(
            profile=self.profile1,
            task=self.task
        )
        self.profile_task.status = ProfileTask.APPLIED
        self.profile_task.save()
        self.task.status = Task.OPEN
        self.task.save()
    
    def test_applicant_accept(self):
        """ Accept an application.
            Change profiletask status to assigned.
            ID: UT-M08.01
        """
        token = api_login(self.profile2.user)
        url = reverse('task-accept-applicant', kwargs={'task_id':self.task.id})
        data = {'profile': self.profile1.id}
        # Shortlist the application
        self.client.post(url, data, format="json", HTTP_AUTHORIZATION='Token {}'.format(token)).data
        # Get the profile task with updated status
        profile_task = ProfileTask.objects.get(task=self.task, profile=self.profile1)
        # Status of profile task should now be REJECTED
        self.assertEqual(profile_task.status, ProfileTask.ASSIGNED)     
        

class TestRating(APITestCase):
    """ Model tests for rating a profile """
    
    def setUp(self):
        """ Create some profiles, tasks and profile_tasks """
        self.poster1 = create_profile(1)
        self.poster2 = create_profile(2)
        self.helper = create_profile(3)
        self.task1 = create_task(self.poster1, 1)
        self.task2 = create_task(self.poster2, 2)
        self.profile_task1 = ProfileTask.objects.create(
            profile=self.helper,
            task=self.task1
        )
        self.profile_task2 = ProfileTask.objects.create(
            profile=self.helper,
            task=self.task2
        )
        self.task1.status = Task.COMPLETE
        self.task2.status = Task.COMPLETE
        self.profile_task1.status = ProfileTask.ASSIGNED
        self.profile_task2.status = ProfileTask.ASSIGNED
        self.task1.helper = self.helper
        self.task2.helper = self.helper
        self.task1.save()
        self.task2.save()
        self.profile_task1.save()
        self.profile_task2.save()
        
    def test_rating(self):
        """ Rate a user twice to check the average is correct.
            User rating should be the average of both ratings.
            ID: UT-M09.01
        """
        token1 = api_login(self.poster1.user)
        token2 = api_login(self.poster2.user)
        url1 = reverse('rate-helper', kwargs={'task_id': self.task1.id})
        url2 = reverse('rate-helper', kwargs={'task_id': self.task2.id})
        # Poster 1 rates the Helper a 5
        data1 = {'profile': self.helper.id, 'rating': 5}
        # Poster 2 rates the Helper a 3
        data2 = {'profile': self.helper.id, 'rating': 3}
        self.client.post(url1, data1, format="json", HTTP_AUTHORIZATION='Token {}'.format(token1))
        self.client.post(url2, data2, format="json", HTTP_AUTHORIZATION='Token {}'.format(token2))
        helper = Profile.objects.get(pk=self.helper.id)
        # Average rating of helper should be a 4
        self.assertEqual(helper.rating, 4.00)
        
        
class TestComplete(APITestCase):
    """ Model tests for completing a task """
    
    def setUp(self):
        """ Create some profiles, tasks and profiletasks """
        self.poster = create_profile(1)
        self.helper = create_profile(2)
        self.task = create_task(self.poster, 1)
        self.profile_task = ProfileTask.objects.create(
            profile=self.helper,
            task=self.task
        )
        self.task.status = Task.IN_PROGRESS
        self.task.skills = [create_skill("python")]
        self.profile_task.status = ProfileTask.ASSIGNED
        self.task.helper = self.helper
        self.task.save()
        self.profile_task.save()
    
    def test_complete(self):
        """ Complete a task that is in progress.
            This should change status to complete and increment the helpers
            number of tasks completed.
            ID: UT-M10.01
        """
        token = api_login(self.poster.user)
        url = reverse('task-complete')
        data = {'task_id': self.task.id}
        self.client.post(url, data, format="json", HTTP_AUTHORIZATION='Token {}'.format(token))
        task = Task.objects.get(pk=self.task.id)
        helper = Profile.objects.get(pk=self.helper.id)
        self.assertEqual(task.status, Task.COMPLETE)
        self.assertEqual(helper.tasks_completed, 1)

class TestDeleteTask(APITestCase):
    """ Model tests for deleting a task """
    
    def setUp(self):
        """ Create some profiles and a task """
        self.poster = create_profile(1)
        self.not_poster = create_profile(2)
        self.task = create_task(self.poster, 1)
    
    def test_delete_task_owner(self):
        """ Delete a task when the task owner.
            This should remove the task.
            ID: UT-M11.01
        """
        self.assertEqual(len(Task.objects.all()), 1)
        token = api_login(self.poster.user)
        url = reverse('task-delete', kwargs={'task_id': self.task.id})
        self.client.post(url, format="json", HTTP_AUTHORIZATION='Token {}'.format(token))
        self.assertEqual(len(Task.objects.all()), 0)
        
    def test_delete_task_not_owner(self):
        """ Delete a task when not the task owner.
            This should not delete the task.
            ID: UT-M11.02
        """
        self.assertEqual(len(Task.objects.all()), 1)
        token = api_login(self.not_poster.user)
        url = reverse('task-delete', kwargs={'task_id': self.task.id})
        self.client.post(url, format="json", HTTP_AUTHORIZATION='Token {}'.format(token))
        self.assertEqual(len(Task.objects.all()), 1)    


class TestUpdateSkills(APITestCase):
    """ Model tests for updating skills """
    
    def setUp(self):
        """ Create some profiles, skills and profileskills """
        self.profile = create_profile(0)
        self.skill1 = create_skill("Python")
        self.skill2 = create_skill("PHP")
        self.skill3 = create_skill("HTML")
        self.profile_skill1 = ProfileSkill.objects.create(
            skill=self.skill1,
            profile=self.profile
        )
        self.profile_skill2 = ProfileSkill.objects.create(
            skill=self.skill2,
            profile=self.profile
        )
    
    def test_update_skills(self):
        """ Update skills with new skill ids.
            This should override the current profileskills with the new ones.
            ID: UT-M12.01
        """
        current_skills = ProfileSkill.objects.filter(profile=self.profile)
        self.assertEqual(len(current_skills), 2)
        token = api_login(self.profile.user)
        data = {'skills': [self.skill3.id]}
        url = reverse('update-skills')
        self.client.put(url, data, format="json", HTTP_AUTHORIZATION='Token {}'.format(token))
        current_skills = ProfileSkill.objects.filter(profile=self.profile)
        self.assertEqual(len(current_skills), 1)
        self.assertEqual(current_skills[0].skill.title, "HTML")    