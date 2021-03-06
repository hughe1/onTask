"""job_bilby Views for the Jobs application

Defines all views; scripts run at each URL.

This file belongs to the back end source code for team 'job-bilby' for the
University of Melbourne subject SWEN90014 Masters Software Engineering Project.
The project is a mobile-first web application for sharing tasks.
The back-end is based on the REST Framework for Django.

Client: Paul Ashkar (Capgemini)                 paul.ashkar@capgemini.com
Supervisor: Rachel Burrows                      rachel.burrows@unimelb.edu.au
Team:
Annie Zhou:                                     azhou@student.unimelb.edu.au
David Barrell:                                   dbarrell@student.unimelb.edu.au
Grace Johnson:                                  gjohnson1@student.unimelb.edu.au
Hugh Edwards:                                   hughe@student.unimelb.edu.au
Matt Perrot:                                    mperrott@student.unimelb.edu.au
View our 'Project Overview' document on Confluence for more information about the project.
Date project started: 6/8/2017
Date project completed: 15/10/2017
"""
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
import django_filters.rest_framework
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from random import randint
import operator
from jobs.models import *
from jobs.models import ProfileSkill as ProfileSkillModel
from jobs.serializers import *
import datetime
from django.utils.timezone import now


class ProfileList(generics.ListAPIView):
    """ List all profiles """
    queryset = Profile.objects.all()
    serializer_class = ProfileUserSerializer


class UserUpdate(generics.UpdateAPIView):
    """ Update the user information """
    queryset = User.objects.all()
    serializer_class = UserPutSerializer

    def get_serializer(self, *args, **kwargs):
        kwargs['partial'] = True
        return super(UserUpdate, self).get_serializer(*args, **kwargs)


class ProfileDetail(generics.RetrieveUpdateAPIView):
    """ Get the information from one profile """
    queryset = Profile.objects.all()
    serializer_class = ProfileUserSerializer

    def get_serializer(self, *args, **kwargs):
        kwargs['partial'] = True
        return super(ProfileDetail, self).get_serializer(*args, **kwargs)


@permission_classes((IsAuthenticated, ))
class HelperTaskList(generics.ListAPIView):
    """ Shows ProfileTasks for which the logged user is a helper
        Filters by status (applied, shortlisted, assigned, ...),
        based on querystring.
    """
    filter_backends = (DjangoFilterBackend,)
    serializer_class = ProfileTaskGetSerializer

    def get_queryset(self):
        """ Gets queryset for the view.
            Filtered by status (from querystring), owner (from logged in user)
    """
        # Filter ProfileTasks by user
        profile = self.request.user.profile.id
        queryset = ProfileTask.objects.filter(profile=profile)

        #Filter ProfileTasks by status
        status = self.request.query_params.get('status', None)
        if status is not None:
            queryset = queryset.filter(status=status)

        return queryset

@permission_classes((IsAuthenticated, ))

class PosterTaskList(generics.ListAPIView):
    """ Shows tasks for which the logged user is the poster
        Filters by Task status based on querystring
    """

    filter_backends = (DjangoFilterBackend,)
    serializer_class = TaskGetSerializer

    def get_queryset(self):
        """ Gets queryset for the view.
        Filtered by status (from querystring), owner (from logged in user)
        """
        #Filter by owner
        profile = self.request.user.profile.id
        queryset = Task.objects.filter(owner=profile)

        #Filter by status
        status = self.request.query_params.get('status', None)
        if status is not None:
            queryset = queryset.filter(status=status)

        return queryset


class ProfileTaskDetail(generics.RetrieveAPIView):
    """ Get the information from one ProfileTask """
    queryset = ProfileTask.objects.all()
    serializer_class = ProfileTaskGetSerializer


class TaskList(generics.ListAPIView):
    """ Get the list of Open tasks relevant for user
        Ranked by relevance
    """
    queryset = Task.objects.all()
    serializer_class = TaskGetSerializer

    #set the view to be searchable and filterable
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    search_fields = ('title','location','description','owner__user__first_name', 'owner__user__last_name', 'skills__title')
    ordering = ('-created_at',)


    def get_queryset(self):
        """ Get the queryset for the view
            Filtered by search
            Ordered by relevance
        """

        # Set initial queryset to all open tasks
        queryset = Task.objects.filter(status=Task.OPEN)

        # Find all profiletasks associated with the current user
        profile_id = self.request.user.profile.id
        my_profiletasks = ProfileTask.objects.filter(profile=profile_id)

        # Filter out all tasks which have a Profiletask associated with the current user
        # i.e. shortlisted, discarded, applied, etc, tasks won't be displayed
        for profiletask in my_profiletasks:
            task = profiletask.task.id
            queryset = queryset.exclude(id=task)

        return queryset


    def filter_queryset(self, queryset):
        # First sort by most recent
        queryset = super(TaskList, self).filter_queryset(queryset)
        #sort the queryset (only if user logged in)
        if self.request.user.is_authenticated():
            for item in queryset:

                # temporarily sets the display_rank of each task
                set_rank(item, self.request)
                pass

            # Firstly sort by most recent, then relevance
            # This means ties in display_rank are resolved by which is
            # more recent
            queryset = sorted(queryset, key=operator.attrgetter('display_rank'), reverse=True)

        return queryset


def set_rank(task, request):
    """ Temporarily sets the display_rank of a task
        based on skills and location. Does not save to the database.
        Display rank is based on skills and location in common with logged
        in user.
    """
    rank = 0

    # List of skills listed by the task
    task_skills = Skill.objects.filter(task__id=task.id)

    # List of skills listed by the logged in user
    profileskill_objs = ProfileSkillModel.objects.filter(profile__id=request.user.profile.id)

    # Add 1 point rank per common skill
    # Take 1 point off per missing skill in profile
    profile_skills = []
    for profile_skill in profileskill_objs:
        profile_skills.append(profile_skill.skill)

    for task_skill in task_skills:
        if task_skill in profile_skills:
            rank += 1
        else:
            rank -=1

    # Add 3 offer if same location as user
    if task.location.lower() == request.user.profile.location.lower():
        rank += 3

    # Temporarily set the rank of the task
    # Does not save to database
    task.display_rank = rank


class TaskDetail(generics.RetrieveAPIView):
    """ Get the information from one Task """
    queryset = Task.objects.all()
    serializer_class = TaskGetSerializer


@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def shortlist_task(request):
    """ Shortlists a task , if it is possible to do so
        task id provided in POST data.
    """
    if request.method == 'POST':

        profile = request.user.profile.id
        request.data["profile"] = profile
        task_id = request.data['task']
        task = get_object_or_404(Task, pk=task_id)

        # Integrity check: makes sure owner is not shortlister
        if profile == task.owner.id:
            return Response({"error":"A profile cannot shortlist their own task!"}, status=status.HTTP_400_BAD_REQUEST)

        # Integrity check: Ensures no ProfileTask exists already for the
        # Task/Profile combination
        if (ProfileTask.objects.filter(profile=profile, task=task).count()>0):
            return Response({"error":"ProfileTask already exists"}, status=status.HTTP_400_BAD_REQUEST)

        # Create and save serializer
        serializer = ProfileTaskPostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def current_profile(request):
    """ Get profile information for the currently logged in user """
    serializer = ProfileUserGetSerializer(request.user.profile, context={"request": request})

    return Response(serializer.data)


# Written so that any task can be discarded, regardless of status.
# May need to be updated if we want 'in progress' tasks to not be discarded.
# need to add permission integrity
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def discard_task(request):
    """ Discard a task
        This removes it from the visible task list available to Helpers.
        task id provided in POST data.
    """
    if request.method == 'POST':

        profile = request.user.profile.id
        request.data["profile"] = profile
        task = request.data['task']

        # Set status of profiletask to 'discarded'
        request.data['status']=ProfileTask.DISCARDED

        # Integrity check: Task cannot already be discarded
        if (ProfileTask.objects.filter(profile=profile, task=task).count()>0):
            profile_task = ProfileTask.objects.filter(profile=profile, task=task)[0]
            if (profile_task.status == 'D'):
                return Response({"error":"ProfileTask has already been discarded."}, status=status.HTTP_400_BAD_REQUEST)

        # If a profileTask already exists for the given profile and task,
        # retrieve it. Otherwise, create a new profiletask
        if (ProfileTask.objects.filter(profile=profile, task=task).count()>0):
            profileTask = ProfileTask.objects.filter(profile=profile, task=task)[0]
            serializer = ProfileTaskPostSerializer(profileTask, data=request.data)
            alreadyExists = True
        else:
            serializer = ProfileTaskPostSerializer(data=request.data)
            alreadyExists = False

        # Save the serializer
        if serializer.is_valid():
            serializer.save()
            if alreadyExists:
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def apply_task(request, task_id):
    """ Apply to a task as a Helper.
        task_id provided as an argument
    """
    if request.method == 'POST':

        profile = request.user.profile.id
        task = get_object_or_404(Task, pk=task_id)

        # Integrity check: task isn't owned by applicant
        if profile == task.owner.id:
            return Response({"error":"A profile cannot apply to their own task!"}, status=status.HTTP_400_BAD_REQUEST)

        # Integrity check: Offer cannot be below 0
        if ('quote' in request.data.keys() and int(request.data['quote']) < 0):
            return Response({"error":"Integrity check failed! Offer cannot be negative."}, status=status.HTTP_400_BAD_REQUEST)


        # Integrity check: More than 1 matching profileTasks should not exist
        if (ProfileTask.objects.filter(profile=profile, task=task_id).count()>1):
            return Response({"error":"Integrity check failed! There should only be one profileTask per profile per task."}, status=status.HTTP_400_BAD_REQUEST)

        # In the case that one matching profileTasks exists
        elif (ProfileTask.objects.filter(profile=profile, task=task_id).count()>0):

            profile_task = get_object_or_404(ProfileTask, profile=profile, task=task_id)

            # Integrity check: Make sure Task is open, and profiletask is
            # shortlisted
            #       Note, this does not mean a profile must have
            #shortlised a task to apply; if a user has not shortlisted the
            # task, then no profiletask will exist (and the other branch
            # of the `if` statement is taken))
            if not (profile_task.status == ProfileTask.SHORTLISTED and task.status == Task.OPEN):
                return Response({"error":"Task must be open, and profile must not have already applied"}, status=status.HTTP_400_BAD_REQUEST)

            # Set compulsory fields for the serializer
            request.data["status"] = ProfileTask.APPLIED
            request.data["datetime_applied"] = now()
            request.data["task"] = profile_task.task.id
            request.data["profile"] = profile_task.profile.id

            # Create serializer from existing profiletask
            serializer = ProfileTaskPostSerializer(profile_task,data=request.data)

        # In the case that no matching profileTask exists, create one
        else:
            # Set compulsory fields for serializer
            request.data["task"] = task_id
            request.data["datetime_applied"] = now()
            request.data["profile"] = profile
            request.data["status"] = ProfileTask.APPLIED

            # Create new serializer
            serializer = ProfileTaskPostSerializer(data=request.data)

        # Save serializer
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def reject_application(request):
    """ Reject an applicant for a task
        profiletask_id retrieved from POST data
    """
    if request.method == 'POST':

        profile_task = get_object_or_404(ProfileTask, pk=request.data["profiletask_id"])
        task = profile_task.task

        # Permission check: logged in user owns the task
        if task.owner.id != request.user.id:
            return Response({"error":"Current User does not own this task"}, status=status.HTTP_400_BAD_REQUEST)

        # Integrity check: profileTask must be either applied or
        # application_shortlisted, and task must be open
        if not ((profile_task.status == ProfileTask.APPLIED or profile_task.status == ProfileTask.APPLICATION_SHORTLISTED)
            and task.status == 'O'):
            return Response({"error":"profileTask status must be (Applied or Application_Shortlisted), and task status must be Open"}, status=status.HTTP_400_BAD_REQUEST)

        #set compulsory fields for the serializer
        request.data["status"] = ProfileTask.REJECTED
        request.data["task"] = profile_task.task.id
        request.data["profile"] = profile_task.profile.id

        # Create and save serializer
        serializer = ProfileTaskPostSerializer(profile_task,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def shortlist_application(request):
    """ Shortlist an application for a task that is posted by the user
        profile and task ids are retrieved from POST data.
    """
    if request.method == 'POST':

        profile_task = get_object_or_404(ProfileTask, pk=request.data["profiletask_id"])
        profile = profile_task.profile
        task = profile_task.task

        # Permission check: Task owner is logged in user
        if task.owner.id != request.user.id:
            return Response({"error":"Current User does not own this task"}, status=status.HTTP_400_BAD_REQUEST)

        # Integrity Check: ProfileTask must be applied and task must be open
        if not (profile_task.status == ProfileTask.APPLIED and task.status == Task.OPEN):
            return Response({"error":"profileTask status must be Applied, and task status must be Open"}, status=status.HTTP_400_BAD_REQUEST)

        # Increment number of shortlists on profile and save
        profile.shortlist()
        profile.save()

        # Set compulsory fields for the serializer
        request.data["status"] = ProfileTask.APPLICATION_SHORTLISTED
        request.data["task"] = profile_task.task.id
        request.data["profile"] = profile_task.profile.id

        # Create and save serializer
        serializer = ProfileTaskPostSerializer(profile_task,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def create_profile(request):
    """ Create a new profile """
    if request.method == 'POST':

        # Make the user. Django auto creates Profile here.
        user_serializer = UserSerializer(data=request.data, context={"request": request})
        if not user_serializer.is_valid():
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user = user_serializer.save()

        # Set user password (needs to be done separately from serializer)
        password = request.data["password"]
        user.set_password(password)
        user.save()

        # Update attached Profile with serializer data. Save serializer.
        request.data["user"] = user.id
        profile = Profile.objects.get(user=user.id)
        profile_serializer = ProfileSerializer(profile, data=request.data, context={"request": request})
        if not profile_serializer.is_valid():
            user.delete()
            return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        profile_serializer.save()

        return Response(user_serializer.data, status=status.HTTP_201_CREATED)


@api_view(['PUT'])
@permission_classes((IsAuthenticated, ))
def password_reset(request):
    """ Reset password """
    user = request.user
    password = request.data["password"]
    print(password)
    try:
        user.set_password(password)
        user.save()
        return Response({"success":"Password changed successfully"}, status=status.HTTP_200_OK)
    except:
        return Response({"error":"Failed to update password"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def create_task(request):
    """ Create a new task """
    if request.method == 'POST':

        # Get skill objects from skill codes in request
        skills = Skill.objects.filter(code__in=request.data["skills"])

        # Add skills to request
        skills_pks = []
        for skill in skills:
            skills_pks.append(skill.pk)
        request.data["skills"] = skills_pks

        # Set task owner to logged in user
        request.data["owner"] = request.user.profile.id

        # Create and save serializer
        task_serializer = TaskPostSerializer(data=request.data)
        if not task_serializer.is_valid():
            return Response(task_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        task_serializer.save()
        return Response(task_serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def complete_task(request):
    """ Mark a Task as Completed. To be called when the Poster judges it do be
    finished.
    task_id retrieved from POST data.
    """
    if request.method == 'POST':

        task = get_object_or_404(Task, pk=request.data["task_id"])
        helper = task.helper

        # Integrity Check: Task should be in progress
        if task.status != Task.IN_PROGRESS:
            return Response({"error":"Task is not In Progress and cannot be Completed"}, status=status.HTTP_400_BAD_REQUEST)
        # Permission check: Logged in user is task owner
        if task.owner.id != request.user.id:
            return Response({"error":"Current User does not own this task"}, status=status.HTTP_400_BAD_REQUEST)

        # Fill in required serializer data, populated from the existing Task
        # data
        old_serializer = TaskPostSerializer(task)
        new_data = old_serializer.data
        new_data["status"] = Task.COMPLETE

        # Create and save the serializer
        serializer = TaskPostSerializer(task,data=new_data)
        if serializer.is_valid():
            serializer.save()
            # Update the number of tasks completed by helper
            if helper:
                helper.complete_task()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def view_applicants(request, task_id):
    """ View applicants of a given task
        Filtered by application status
        Ranked by Profile rating
        task_id provided as an argument
    """
    if request.method == 'GET':

        filter_backends = (DjangoFilterBackend,)
        task = get_object_or_404(Task, pk=task_id)
        requester = request.user.profile
        owner = Task.objects.get(pk=task_id).owner

        # Permission Check: Check requester is the task owner
        if not requester == owner:
            return Response({"error":"Cannot view applicants as not task owner"}, status=status.HTTP_400_BAD_REQUEST)

        # Get the ProfileTasks for the task
        profile_tasks = ProfileTask.objects.filter(task=task_id)

        #Filter by status
        profiletask_status = request.query_params.get('status', None)
        if profiletask_status is not None:
            profile_tasks = profile_tasks.filter(status=profiletask_status)

        #Sort by Profile rating
        profile_tasks = sorted(profile_tasks, key=operator.attrgetter('profile.rating'),reverse=True)

        # Return serialized list of applicants
        serializer = ApplicantSerializer(profile_tasks, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


# View applicants of a task, filtered by application status
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def delete_task(request, task_id):
    """ Delete a task
        task_id provided as an argument
    """
    if request.method == 'POST':

        task = get_object_or_404(Task, pk=task_id)
        requester = request.user.profile
        owner = Task.objects.get(pk=task_id).owner

        # Permission Check: Check requester is the task owner
        if not requester == owner:
            return Response({"error":"Cannot delete task: not task owner"}, status=status.HTTP_400_BAD_REQUEST)

        # Delete the task
        deleted = task.delete()
        return Response(deleted, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def accept_applicant(request, task_id):
    """ Accepts an applicant for a task. Sets task to 'in progress'
        Task_id provided as an argument
        Applicant id provided in POST data as "profile"
    """

    task = get_object_or_404(Task, pk=task_id)
    applicant = get_object_or_404(Profile, pk=request.data["profile"])

    #Permission Check: Ensures correct user is accepting applicant
    if task.owner.id != request.user.id:
        return Response({"error":"Current User does not own this task"}, status=status.HTTP_400_BAD_REQUEST)

    # Integrity check: Check the task is Open and does not have a helper
    if (task.status != Task.OPEN or task.helper != None):
        return Response({"error":"Task must be open, and have no helper assigned"}, status=status.HTTP_400_BAD_REQUEST)

    # Integrity Check: Check that the helper has submitted an application
    # for the task
    if ((ProfileTask.objects.filter(profile=applicant, task=task).count()<1) or
        (ProfileTask.objects.filter(profile=applicant, task=task)[0].status != ProfileTask.APPLIED and
        ProfileTask.objects.filter(profile=applicant, task=task)[0].status != ProfileTask.APPLICATION_SHORTLISTED)) :
        return Response({"error":"Profile must have applied for task to be accepted"}, status=status.HTTP_400_BAD_REQUEST)

    # Set required fields for serializer, populating fro existing task
    old_serializer = TaskPostSerializer(task)
    new_data = old_serializer.data
    new_data["status"] = Task.IN_PROGRESS
    profile_serializer = ProfileSerializer(applicant)
    new_data["helper"] = applicant.pk

    #Create and save new serializer
    serializer = TaskPostSerializer(task, data=new_data)
    if serializer.is_valid():
        serializer.save()

        # Update the status of the associated profiletask
        profileTask = ProfileTask.objects.filter(profile=applicant, task=task)[0]
        profileTask.status = ProfileTask.ASSIGNED
        profileTask.save()

        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def rate_helper(request, task_id):
    """ Rates a helper after a task has been completed
        Task_id provided as an argument
        Rating provided by POST data
    """

    task = get_object_or_404(Task, pk=task_id)
    applicant = get_object_or_404(Profile, pk=request.data["profile"])
    rating = int(request.data["rating"])

    #Integrity check: Rating must be an integer
    if not isinstance(rating, int):
        return Response ({"error": "Rating must be and integer value"}, status=status.HTTP_400_BAD_REQUEST)

    #Integrity check: Rating must be between 0 and 5
    if not (rating >= 0 and rating <=5):
        return Response ({"error": "Rating must be between 0 and 5"}, status=status.HTTP_400_BAD_REQUEST)

    #Permission check: Rater is task owner
    if task.owner.id != request.user.id:
        return Response({"error":"Current User does not own this task"}, status=status.HTTP_400_BAD_REQUEST)

    # Integrity check: Check the task is complete
    if task.status != Task.COMPLETE:
        return Response({"error":"Task must be complete to rate user"}, status=status.HTTP_400_BAD_REQUEST)

    # Integrity check: Check that the helper is assigned to the task
    if ((ProfileTask.objects.filter(profile=applicant, task=task).count()<1)
        or (ProfileTask.objects.filter(profile=applicant, task=task)[0].status != ProfileTask.ASSIGNED)
        or task.helper != applicant):
            return Response({"error":"Profile must be assigned to task to be rated"}, status=status.HTTP_400_BAD_REQUEST)

    # Fill in compulsory fields for serializer
    profile_task = ProfileTask.objects.filter(profile=applicant, task=task)[0]
    old_serializer = ProfileTaskPostSerializer(profile_task)
    new_data = old_serializer.data
    new_data["rating"] = rating

    # Create and save new serializer
    serializer = ProfileTaskPostSerializer(profile_task, data=new_data)
    if serializer.is_valid():
        serializer.save()
        # Update the applicants average rating
        applicant.update_rating()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def number_applications_today(profile_id):
    """ Returns the number of applications made by the given profile
        in the past 24 hours.
    """

    # Get all profiletasks by the user
    profile = get_object_or_404(Profile, pk=profile_id)
    applications = ProfileTask.objects.filter(profile=profile)

    interval = datetime.timedelta(days=1)

    recent_applications = 0

    # Count the number of applications in the past day
    for app in applications:
        if app.datetime_applied is not None:
            if now() - app.datetime_applied < interval:
                recent_applications +=1
    return recent_applications

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def under_application_limit(request):
    """ Returns whether the current profile is under their daily limit
        of task applications
    """
    under_limit = True
    profile = request.user.profile

    # Define the application limit for each (rounded down) average profile rating
        # Key: rating threshold
        # Value: Daily application limit
    rating_limits = {
        5 : 20,
        4 : 20,
        3 : 15,
        2 : 10,
        1 : 5,
        0 : 2,
    }

    #rating_threshold is the profile's rounded down rating
    rating_threshold = int(profile.rating)

    # set the application limit, based on rating_threshold
    if rating_threshold in rating_limits.keys():
        application_limit = rating_limits[rating_threshold]
    else:
        return Response({"error":"Invalid user rating!"}, status=status.HTTP_400_BAD_REQUEST)

    # Calculate whether today's applications exceed the limit
    number_applications = number_applications_today(profile.id)

    if number_applications >= application_limit:
        under_limit = False

    return Response({"under_application_limit":str(under_limit)}, status=status.HTTP_200_OK)


class SkillList(generics.ListAPIView):
    """ List all skills """
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer


@api_view(['PUT'])
def update_skills(request):
    """ Takes a list of skills and updates the ProfileSkills with that
        list of skills by deleting old skills first.
    """

    profile = request.user.profile
    skills = request.data["skills"]
    profile_skills = ProfileSkillModel.objects.all()
    # Gather info for new skills to be updated on profile
    profile_skill_data = {}
    profile_skill_data["profile"] = profile.id

    # Check that each skill in list is valid before deleting old ProfileSkills
    for skill_id in skills:
        try:
            skill = Skill.objects.get(pk=skill_id)
        except:
            return Response({"error":"All skill id's must exist in database"},status=status.HTTP_400_BAD_REQUEST)

    # Delete old profile skills
    ProfileSkillModel.objects.filter(profile=profile).delete()

    # Update the ProfileSkill for each skill listed
    for skill_id in skills:
        # Try getting skill. If it can't be found try block fails.
        skill = Skill.objects.get(pk=skill_id)
        profile_skill_data["skill"] = skill_id
        # Set new ProfileSkill serializer
        serializer = ProfileSkillSerializer(data=profile_skill_data, context={"request": request})
        if serializer.is_valid():
            serializer.save()

    # Updated user data to show updated skills
    profile_serializer = ProfileUserGetSerializer(profile, context={"request": request})

    return Response(profile_serializer.data,status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def completed_tasks(request, profile_id):
    """ Gets the list of ProfileTasks a helper has completed """
    profile = get_object_or_404(Profile, pk=profile_id)
    profile_tasks = ProfileTask.objects.filter(profile=profile)
    completed_tasks = []
    for pt in profile_tasks:
        if (pt.task.status == Task.COMPLETE and pt.status == ProfileTask.ASSIGNED):
            completed_tasks.append(pt)

    serializer = ProfileTaskGetSerializer(completed_tasks, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
