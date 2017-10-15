from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from jobs.models import Profile, User, Task, ProfileTask, ProfileSkill
from jobs.serializers import TaskGetSerializer, TaskPostSerializer
from jobs.tests.test_helper import *
from jobs.views import number_applications_today
from django.utils.timezone import now

"""
Note: The coding style followed for these unit tests is deliberately very
verbose. It does not follow a DRY coding style, but a DAMP coding style
to increase the readability of tests. There is minimal risk associated with
repeated code as each test is isolated. This also allows small tweaks to be
made to tests that are similar but not exactly the same.
https://stackoverflow.com/questions/6453235/what-does-damp-not-dry-mean-when-talking-about-unit-tests
"""


class ProfileTests(APITestCase):
    """ Tests for creating a profile """
    
    def test_create_profile(self):
        """ Ensure we can create a new Profile (and subsequently, User)
            ID: UT-V01.01
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
    """ View tests for listing tasks """
    
    def setUp(self):
        """ Create some task objects and users """
        # Create users
        self.user1 = create_user(1)
        self.user2 = create_user(2)
        self.user3 = create_user(3)
        # Update profile info
        self.profile1 = update_profile(self.user1, 1)
        self.profile2 = update_profile(self.user2, 2)
        self.profile3 = update_profile(self.user3, 3)
        # Create a task without a helper
        self.task1 = Task.objects.create(
            title="Test Task 1",
            description="Description 1",
            offer=0,
            location="Melbourne",
            owner=self.profile1
        )
        # Create a task with a helper
        self.task2 = Task.objects.create(
            title="Test Task 2",
            description="Description 2",
            offer=20,
            location="Sydney",
            owner=self.profile2,
            helper=self.profile1
        )
        # Create a profile task
        self.profile_task = ProfileTask.objects.create(
            profile=self.profile3,
            task=self.task1
        )        
        
    def test_task_list(self):
        """ Test whether the right list of tasks is returned.
            This should return both tasks.
            ID: UT-V02.01
        """
        token = api_login(self.user1)
        url = reverse('task-list')
        response = self.client.get(url, format='json', HTTP_AUTHORIZATION='Token {}'.format(token))
        self.assertEqual(len(response.data), 2)

    def test_task_list_qstring(self):
        """ Test whether the right list of tasks is returned with a search term.
            This should only return 1 task.
            ID: UT-V02.02
        """
        token = api_login(self.user1)
        base_url = reverse('task-list')
        qstring = "?search=Sydney"
        url = base_url + qstring
        response = self.client.get(url, format='json', HTTP_AUTHORIZATION='Token {}'.format(token))
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["location"], "Sydney")

    def test_task_list_has_shorlisted(self):
        """ When a user has already shortlisted a task it should not appear in
            the task list.
            This task list should therefore only return 1 of the tasks.            
            ID: UT-V02.03
        """
        token = api_login(self.user3)
        url = reverse('task-list')
        response = self.client.get(url, format='json', HTTP_AUTHORIZATION='Token {}'.format(token))
        self.assertEqual(len(response.data), 1)


class TestTaskCreate(APITestCase):
    """ View tests for creation of tasks """
    
    def setUp(self):
        """ Create users with skills """
        self.user1 = create_user(1)
        self.skill1 = create_skill("Python")
        self.skill2 = create_skill("PHP")
    
    def test_task_create(self):
        """ Test creation of a task.
            All fields are valid so this should work.
            ID: UT-V03.01
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
        # Check all data is correct in response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Task 1")
        self.assertEqual(response.data["description"], "Desc 1")
        self.assertEqual(response.data["offer"], 50)
        self.assertEqual(response.data["location"], "Loc 1")
        self.assertEqual(len(response.data["skills"]), 2)

    def test_task_create_not_valid(self):
        """ Test creation of a task without all valid fields.
            This should not create a task.
            ID: UT-V03.02
        """
        token = api_login(self.user1)
        url = reverse('task-create')
        data = {
                  'description' : 'Desc 1',
                  'offer' : 50,
                  'location' : 'Loc 1',
                  'is_remote' : True,
                  'skills': [self.skill1.code, self.skill2.code]
                }
        response = self.client.post(url, data, format="json", HTTP_AUTHORIZATION='Token {}'.format(token))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
class TestShortlist(APITestCase):
    """ View tests for shortlisting a task as a helper """
    
    def setUp(self):
        """ Create some profiles and tasks """
        self.profile1 = create_profile(1)
        self.task1 = create_task(self.profile1, 1)
        self.profile2 = create_profile(2)
        self.task2 = create_task(self.profile2, 2)
        
    # Ensure a user can shortlist a task they have not already shortlisted
    def test_shortlist_not_already_shortlisted(self):
        """ Shortlist a task that has not already been shortlisted.
            This is allowed and should create a ProfileTask object.
            ID: UT-V04.01
        """
        token = api_login(self.profile1.user)
        url = reverse('task-shortlist')
        data = {'task': self.task2.id}
        response = self.client.post(url, data, format="json", HTTP_AUTHORIZATION='Token {}'.format(token))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
    # Ensure a user cannot shortlist a task they have already shortlisted    
    def test_shortlist_already_shortlisted(self):
        """ Shortlist a task that has already been shortlisted.
            The first shorlist is allowed, but the second is not.
            ID: UT-V04.02
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
    """ View tests for discarding a task as a helper """
    
    def setUp(self):
        """" Create some profiles and some tasks """
        self.profile1 = create_profile(1)
        self.task1 = create_task(self.profile1, 1)
        self.profile2 = create_profile(2)
        self.task2 = create_task(self.profile2, 2)
        
    # Ensure a user can discard a task they have not already discarded
    def test_discard_not_already_discarded(self):
        """ Discard a task that hasn't already been discarded (or shortlisted).
            This is allowed and should create a ProfileTask.
            ID: UT-V05.01
        """
        token = api_login(self.profile1.user)
        url = reverse('task-discard')
        data = {'task': self.task1.id}
        response = self.client.post(url, data, format="json", HTTP_AUTHORIZATION='Token {}'.format(token))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
    # Ensure a user cannot discard a task they have already discarded    
    def test_discard_already_discarded(self):
        """ Try discarding a task that has already been discarded.
            This is not allowed.
            ID: UT-V05.02
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
    """ View tests for applying for a task """
    
    def setUp(self):
        """ Create some profiles and tasks """
        self.profile1 = create_profile(1)
        self.task1 = create_task(self.profile1, 1)
        self.profile2 = create_profile(2)
        self.task2 = create_task(self.profile2, 2)
        
    def test_apply_unshortlisted(self):
        """ Apply for a task that hasn't been shortlisted yet.
            This is allowed.
            ID: UT-V06.01
        """
        token = api_login(self.profile2.user)
        url = reverse('task-apply', kwargs={'task_id': self.task1.id})
        data = {
        #   "profiletask_id" : "1",
          "answer1" : "ans1",
          "answer2" : "ans2",
          "answer3" : "ans3"
        }
        response = self.client.post(url, data, format="json", HTTP_AUTHORIZATION='Token {}'.format(token))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
    def test_apply_discarded(self):
        """ Test applying to a task that has already been discarded.
            This is not allowed.
            ID: UT-V06.02
        """
        #discard the task
        token = api_login(self.profile2.user)
        url = reverse('task-discard')
        data = {'task': self.task1.id}
        response = self.client.post(url, data, format="json", HTTP_AUTHORIZATION='Token {}'.format(token))
        url = reverse('task-apply', kwargs={'task_id': self.task1.id})
        # self.profile_task1 = ProfileTask.objects.filter(profile=self.profile1, task=self.task1)[0]
        data = {
        #   "profiletask_id" : self.profile_task1.id,
          "answer1" : "ans1",
          "answer2" : "ans2",
          "answer3" : "ans3"
        }
        response = self.client.post(url, data, format="json", HTTP_AUTHORIZATION='Token {}'.format(token))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_apply_shortlisted(self):
        """ Apply to a task that has already been shortlisted.
            This is not allowed.
            ID: UT-V06.03
        """
        # Shortlist the task
        token = api_login(self.profile2.user)
        url = reverse('task-shortlist')
        data = {'task': self.task1.id}
        response = self.client.post(url, data, format="json", HTTP_AUTHORIZATION='Token {}'.format(token))
        url = reverse('task-apply', kwargs={'task_id': self.task1.id})
        data = {
          "answer1" : "ans1",
          "answer2" : "ans2",
          "answer3" : "ans3"
        }
        # First apply - should pass
        response = self.client.post(url, data, format="json", HTTP_AUTHORIZATION='Token {}'.format(token))
        # Shortlisting a task creates a ProfileTask hence the 201 Status code
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Attempt to reapply - should fail
        response = self.client.post(url, data, format="json", HTTP_AUTHORIZATION='Token {}'.format(token))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_apply_own_task(self):
        """ Apply for a task that a user owns. 
            A profile can't apply to its own task.
            ID: UT-V06.04
        """
        token = api_login(self.profile2.user)
        url = reverse('task-apply', kwargs={'task_id': self.task2.id})
        data = {
          "answer1" : "ans1",
          "answer2" : "ans2",
          "answer3" : "ans3"
        }
        response = self.client.post(url, data, format="json", HTTP_AUTHORIZATION='Token {}'.format(token))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
class TestRejectApplication(APITestCase):
    """ View tests for rejecting an application. """

    def setUp(self):
        """ Create some profiles, profile tasks and tasks """
        self.poster = create_profile(1)
        self.helper = create_profile(2)
        self.not_poster = create_profile(3)
        self.task = create_task(self.poster, 1)
        self.profile_task = ProfileTask.objects.create(
            profile=self.helper,
            task=self.task
        )
        self.profile_task.status = ProfileTask.APPLIED
        self.profile_task.save()

    def test_applicant_reject_not_task_owner(self):
        """ Attempt to reject an applicant when not the task owner.
            This is not allowed.
            ID: UT-V07.01
        """
        token = api_login(self.not_poster.user)
        url = reverse('task-reject_application')
        data = {'profiletask_id': self.profile_task.id}
        response = self.client.post(url, data, format="json", HTTP_AUTHORIZATION='Token {}'.format(token))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_applicant_reject_is_task_owner(self):
        """ Reject an applicant when owner of task.
            This is allowed.
            ID: UT-V07.02
        """
        token = api_login(self.poster.user)
        url = reverse('task-reject_application')
        data = {'profiletask_id': self.profile_task.id}
        # Shortlist the application
        response = self.client.post(url, data, format="json", HTTP_AUTHORIZATION='Token {}'.format(token))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_applicant_reject_hasnt_applied(self):
        """ Attempt to reject an applicant that hasn't applied yet.
            This is not allowed.
            ID: UT-V07.03
        """
        token = api_login(self.poster.user)
        url = reverse('task-reject_application')
        data = {'profiletask_id': self.profile_task.id}
        self.profile_task.status = ProfileTask.SHORTLISTED
        self.profile_task.save()
        # Shortlist the application
        response = self.client.post(url, data, format="json", HTTP_AUTHORIZATION='Token {}'.format(token))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestViewApplicants(APITestCase):
    """ View tests for viewing applicants """
    
    def setUp(self):
        """ Create some profiles and a task """
        self.poster = create_profile(0)
        self.task = create_task(self.poster, 0)
        self.helper1 = create_profile(1)
        self.helper2 = create_profile(2)
        
    def test_view_0_applicants_applied(self):
        """ View applied applicants when 0 have applied.
            This should return an empty list.
            ID: UT-V08.01
        """
        token = api_login(self.poster.user)
        base_url = reverse('task-view-applicants', kwargs={'task_id':self.task.id})
        qstring = "?status={}".format(ProfileTask.APPLIED)
        url = base_url + qstring
        response = self.client.get(url, format="json", HTTP_AUTHORIZATION='Token {}'.format(token))
        self.assertEqual(response.data, [])
    
    def test_view_1_applicants_applied(self):
        """ View applied applicants when 1 has applied.
            This should return a list of 1 person.
            ID: UT-V08.02
        """
        token = api_login(self.poster.user)
        base_url = reverse('task-view-applicants', kwargs={'task_id':self.task.id})
        qstring = "?status={}".format(ProfileTask.APPLIED)
        url = base_url + qstring
        self.profile_task = ProfileTask.objects.create(
            profile=self.helper1,
            task=self.task
        )
        self.profile_task.status = ProfileTask.APPLIED
        self.profile_task.save()
        response = self.client.get(url, format="json", HTTP_AUTHORIZATION='Token {}'.format(token))
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["status"], ProfileTask.APPLIED)

    def test_view_1_applicants_shortlisted(self):
        """ View shortlisted applicants when 1 has been shortlisted.
            This should return a list of 1 person.
            ID: UT-V08.03
        """
        token = api_login(self.poster.user)
        base_url = reverse('task-view-applicants', kwargs={'task_id':self.task.id})
        qstring = "?status={}".format(ProfileTask.SHORTLISTED)
        url = base_url + qstring
        self.profile_task = ProfileTask.objects.create(
            profile=self.helper1,
            task=self.task
        )
        self.profile_task.status = ProfileTask.SHORTLISTED
        self.profile_task.save()
        response = self.client.get(url, format="json", HTTP_AUTHORIZATION='Token {}'.format(token))
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["status"], ProfileTask.SHORTLISTED)
        
    def test_view_2_applicants_shortlisted(self):
        """ View shortlisted applicants when 2 have been shortlisted.
            This should return a list of 2 people.
            ID: UT-V08.04
        """
        token = api_login(self.poster.user)
        base_url = reverse('task-view-applicants', kwargs={'task_id':self.task.id})
        qstring = "?status={}".format(ProfileTask.SHORTLISTED)
        url = base_url + qstring
        self.profile_task1 = ProfileTask.objects.create(
            profile=self.helper1,
            task=self.task
        )
        self.profile_task2 = ProfileTask.objects.create(
            profile=self.helper2,
            task=self.task
        )
        self.profile_task1.status = ProfileTask.SHORTLISTED
        self.profile_task2.status = ProfileTask.SHORTLISTED
        self.profile_task1.save()
        self.profile_task2.save()
        response = self.client.get(url, format="json", HTTP_AUTHORIZATION='Token {}'.format(token))
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["status"], ProfileTask.SHORTLISTED)

    def test_view_1_applicants_assigned(self):
        """ View assigned applicants when 1 has been assigned.
            This should return a list of 1 person.
            ID: UT-V08.05
        """
        token = api_login(self.poster.user)
        base_url = reverse('task-view-applicants', kwargs={'task_id':self.task.id})
        qstring = "?status={}".format(ProfileTask.ASSIGNED)
        url = base_url + qstring
        self.profile_task = ProfileTask.objects.create(
            profile=self.helper1,
            task=self.task
        )
        self.profile_task.status = ProfileTask.ASSIGNED
        self.profile_task.save()
        response = self.client.get(url, format="json", HTTP_AUTHORIZATION='Token {}'.format(token))
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["status"], ProfileTask.ASSIGNED)        


class TestNumberApplications(APITestCase):
    """ View tests for the number of applications """

    def setUp(self):
        """ Create some profile, tasks and profile tasks """
        self.poster = create_profile(0)
        self.task1 = create_task(self.poster, 1)
        self.task2 = create_task(self.poster, 2)
        self.task3 = create_task(self.poster, 3)
        self.helper = create_profile(1)
        # Set rating to 0 to get lowest application limit
        self.helper.rating = 0
        self.helper.save()
        # Create a profile task
        self.profile_task1 = ProfileTask.objects.create(
            profile=self.helper,
            task=self.task1,
            datetime_applied=now()
        )
        self.profile_task1.status = ProfileTask.APPLIED
        self.profile_task1.save()
        
    def test_under_application_limit(self):
        """ Test that someone is under the application limit.
            This should return true.
            ID: UT-V09.01
        """
        token = api_login(self.helper.user)
        url = reverse('under-application-limit')
        response = self.client.get(url, format="json", HTTP_AUTHORIZATION='Token {}'.format(token))
        self.assertEqual(response.data["under_application_limit"], "True")
    
    def test_not_under_application_limit(self):
        """ Test that someone is not under the application limit.
            This should return false.
            ID: UT-V09.02
        """
        token = api_login(self.helper.user)
        url = reverse('under-application-limit')
        self.profile_task2 = ProfileTask.objects.create(
        profile=self.helper,
        task=self.task2,
        datetime_applied=now()
        )
        self.profile_task2.status = ProfileTask.APPLIED
        self.profile_task2.save()
        response = self.client.get(url, format="json", HTTP_AUTHORIZATION='Token {}'.format(token))
        self.assertEqual(response.data["under_application_limit"], "False")
    
    def test_under_application_limit_bad_rating(self):
        """ Test an application for an invalid user rating.
            This should result in an error.
            ID: UT-V09.03
        """
        token = api_login(self.helper.user)
        self.helper.rating = 6
        self.helper.save()
        url = reverse('under-application-limit')
        response = self.client.get(url, format="json", HTTP_AUTHORIZATION='Token {}'.format(token))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        

class TestUpdateSkills(APITestCase):
    """ View tests for updating skills """
    
    def setUp(self):
        """ Create some profiles and skills """
        self.profile = create_profile(0)
        self.skill1 = create_skill("Python")
        self.profile_skill1 = ProfileSkill.objects.create(
            skill=self.skill1,
            profile=self.profile
        )
    
    def test_update_skills(self):
        """ Update to a new skill.
            This should override any skills the profile had and only return the
            skill that was updated.
            ID: UT-V10.01
        """
        token = api_login(self.profile.user)
        data = {'skills': [2]}
        url = reverse('update-skills')
        response = self.client.put(url, data, format="json", HTTP_AUTHORIZATION='Token {}'.format(token))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        
class TestCurrentProfile(APITestCase):
    """ View tests for getting the active users profile """
    
    def setUp(self):
        """ Create a profile """
        self.profile = create_profile(1)
    
    def test_current_profile(self):
        """ Test getting the users current profile.
            This should return the users profile who is logged in.
            ID: UT-V10.02
        """
        token = api_login(self.profile.user)
        url = reverse('profile-current')
        response = self.client.get(url, format="json", HTTP_AUTHORIZATION="Token {}".format(token))
        self.assertEqual(response.data["user"]["username"], "test1_user")
        

class TestUpdateProfile(APITestCase):
    """ Views tests for updating a profile """
    
    def setUp(self):
        """ Create a profile """
        self.profile = create_profile(1)
        
    def test_update_profile(self):
        """ Update a profile with a partial amount of new details.
            This should update the profile and return the all profile details.
            ID: UT-V11.01
        """
        token = api_login(self.profile.user)
        url = reverse('profile-detail', kwargs={"pk":self.profile.id})
        data = {"location": "hobart"}
        response = self.client.put(url, data, format="json", HTTP_AUTHORIZATION="Token {}".format(token))
        self.assertEqual(response.data["location"], "hobart")