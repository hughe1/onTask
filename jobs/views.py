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

from jobs.models import *
from jobs.serializers import *


class ProfileList(generics.ListAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileUserSerializer


class ProfileDetail(generics.RetrieveAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileUserSerializer


#class ProfileTaskList(generics.ListAPIView):
#    queryset = ProfileTask.objects.all()
#    serializer_class = ProfileTaskSerializer


# TODO: insert nested JSON so HelperTask has the Task object info (as well as the ProfileTask)

# Shows profiletasks for which the logged user is a helper
# Filters by status (applied, shortlisted, assigned, ...) based on querystring
@permission_classes((IsAuthenticated, ))

class HelperTaskList(generics.ListAPIView):

    filter_backends = (DjangoFilterBackend,)

    serializer_class = ProfileTaskGetSerializer

    def get_queryset(self):

        profile = self.request.user.profile.id
        queryset = ProfileTask.objects.filter(profile=profile)

        status = self.request.query_params.get('status', None)
        if status is not None:
            queryset = queryset.filter(status=status)

        return queryset

# Shows tasks for which the logged user is the poster
# Filters by status (in progress, open, complete) based on querystring
@permission_classes((IsAuthenticated, ))

class PosterTaskList(generics.ListAPIView):

    filter_backends = (DjangoFilterBackend,)

    serializer_class = TaskGetSerializer

    def get_queryset(self):

        profile = self.request.user.profile.id
        queryset = Task.objects.filter(owner=profile)

        status = self.request.query_params.get('status', None)
        if status is not None:
            queryset = queryset.filter(status=status)

        return queryset


class ProfileTaskDetail(generics.RetrieveAPIView):
    queryset = ProfileTask.objects.all()
    serializer_class = ProfileTaskGetSerializer


class TaskList(generics.ListAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskGetSerializer

    #set the view to be searchable and filterabe
    filter_backends = (filters.SearchFilter,DjangoFilterBackend,)

    # set the fields which are accessed by searching
    search_fields = ('title','location','description','owner__user__first_name', 'owner__user__last_name')

    #Optionally filtered queryset
    def get_queryset(self):

        #set initial queryset to all task objects
        queryset = Task.objects.all()

        #Filter by skills
        #skills are comma separated, ie ?skills=java,python
        skills = self.request.query_params.get('skills', None)
        if skills is not None:
            skills = skills.split(',')
            skill_querysets = []

            #construct individual querysets for each skill
            for skill_str in skills:
                skill = get_object_or_404(Skill, title=skill_str)
                skill_querysets.append(skill.task_set.all())
                
            #find the intersection of all querysets
            for skill_queryset in skill_querysets:
                queryset = queryset & skill_queryset

        #Filter by location
        # __icontains makes query case insensitive and 'contains' rather than 'equals'
        # so ?location=syd will match 'Sydney'
        location = self.request.query_params.get('location', None)
        if location is not None:
            queryset = queryset.filter(location__icontains=location)

        return queryset


class TaskDetail(generics.RetrieveAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskGetSerializer


@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def shortlist_task(request):
    if request.method == 'POST':

        #checks to see if ProfileTask already exists
        profile = request.user.profile.id
        request.data["profile"] = profile
        task = request.data['task']
        if (ProfileTask.objects.filter(profile=profile, task=task).count()>0):
            return Response({"error":"ProfileTask already exists"}, status=status.HTTP_400_BAD_REQUEST)

        #create and save serializer
        serializer = ProfileTaskPostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)


# Written so that any task can be discarded, regardless of status. 
# May need to be updated if we want 'in progress' tasks to not be discarded. 
# need to add permission integrity
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def discard_task(request):
    if request.method == 'POST':

        #checks to see if ProfileTask already exists
        profile = request.user.profile.id
        request.data["profile"] = profile
        task = request.data['task']
        # set status of profiletask to 'discarded'
        request.data['status']=ProfileTask.DISCARDED

        # if task is already discarded, return bad response
        if (ProfileTask.objects.filter(profile=profile, task=task).count()>0):
            profile_task = ProfileTask.objects.filter(profile=profile, task=task)[0]
            if (profile_task.status == 'D'):
                return Response({"error":"ProfileTask has already been discarded."}, status=status.HTTP_400_BAD_REQUEST)

        #if a profileTask already exists for the given profile and task, get it
        # otherwise, create a new profiletask
        if (ProfileTask.objects.filter(profile=profile, task=task).count()>0):

            profileTask = ProfileTask.objects.filter(profile=profile, task=task)[0]
            serializer = ProfileTaskPostSerializer(profileTask, data=request.data)
            alreadyExists = True
        else:
            serializer = ProfileTaskPostSerializer(data=request.data)
            alreadyExists = False

        #save the serializer
        if serializer.is_valid():
            serializer.save()
            if alreadyExists:
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
# TODO:
#need to check here that the user is the logged in user
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def apply_task(request):
    if request.method == 'POST':

        #returns 404 if no such ProfileTask exists
        profile_task = get_object_or_404(ProfileTask, pk=request.data["profiletask_id"])
        task = profile_task.task

        # if task has already been assigned or rejected, return an error
        if not (profile_task.status == 'SL' and task.status == 'O'):
            return Response({"error":"Task isn't available to apply for."}, status=status.HTTP_400_BAD_REQUEST)

        #set status to 'applied'
        request.data["status"] = "AP"

        #set compulsory fields in the serializer
        request.data["task"] = profile_task.task.id
        request.data["profile"] = profile_task.profile.id

        serializer = ProfileTaskPostSerializer(profile_task,data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        print(serializer.errors)
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def reject_application(request):
    if request.method == 'POST':

        #returns 404 if no such ProfileTask exists
        profile_task = get_object_or_404(ProfileTask, pk=request.data["profiletask_id"])
        task = profile_task.task

        if task.owner.id != request.user.id:
            return Response({"error":"Current User does not own this task"}, status=status.HTTP_400_BAD_REQUEST)

        # profileTask must be either applied or application_shortlisted, and task must be open
        if not ((profile_task.status == ProfileTask.APPLIED or profile_task.status == ProfileTask.APPLICATION_SHORTLISTED)
            and task.status == 'O'):
            return Response({"error":"profileTask status must be (Applied or Application_Shortlisted), and task status must be Open"}, status=status.HTTP_400_BAD_REQUEST)

        #set status to 'Rejected'
        request.data["status"] = "R"

        #set compulsory fields in the serializer
        request.data["task"] = profile_task.task.id
        request.data["profile"] = profile_task.profile.id

        serializer = ProfileTaskPostSerializer(profile_task,data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        print(serializer.errors)
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def shortlist_application(request):
    if request.method == 'POST':

        #returns 404 if no such ProfileTask exists
        profile_task = get_object_or_404(ProfileTask, pk=request.data["profiletask_id"])
        task = profile_task.task

        if task.owner.id != request.user.id:
            return Response({"error":"Current User does not own this task"}, status=status.HTTP_400_BAD_REQUEST)

        # profileTask must be  applied and task must be open
        if not (profile_task.status == ProfileTask.APPLIED and task.status == 'O'):
            return Response({"error":"profileTask status must be Applied, and task status must be Open"}, status=status.HTTP_400_BAD_REQUEST)

        #set status to 'Application shortlisted'
        request.data["status"] = "ASL"

        #set compulsory fields in the serializer
        request.data["task"] = profile_task.task.id
        request.data["profile"] = profile_task.profile.id

        serializer = ProfileTaskPostSerializer(profile_task,data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        print(serializer.errors)
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def create_profile(request):
    if request.method == 'POST':

        #make the user
        user_serializer = UserSerializer(data=request.data)
        if not user_serializer.is_valid():
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user = user_serializer.save()

        #set user password (needs to be done separately from serializer)
        password = request.data["password"]
        user.set_password(password)
        user.save()

        #update attached profile with serializer data
        request.data["user"] = user.id
        profile = Profile.objects.get(user=user.id)
        profile_serializer = ProfileSerializer(profile,data=request.data)
        if not profile_serializer.is_valid():
            user.delete()
            return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        profile_serializer.save()

        return Response(user_serializer.data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def create_task(request):
    if request.method == 'POST':
        
        # Get skill objects from skill code
        skills = Skill.objects.filter(code__in=request.data["skills"])
        skills_pks = []
        # Get the skill pk's and add to a a list
        for skill in skills:
            skills_pks.append(skill.pk)
        # Add skill pk's to the request
        request.data["skills"] = skills_pks
        request.data["owner"] = request.user.profile.id
        task_serializer = TaskPostSerializer(data=request.data)
        if not task_serializer.is_valid():
            return Response(task_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # Save task serializer and create new Task object
        task_serializer.save()
        return Response(task_serializer.data, status=status.HTTP_201_CREATED)


########
### DEPRECATED METHOD - NOW ALL DONE IN ACCEPT_APPLICANT
#######

# Sets the status of task to "in progress"
# Should be called as soon as applicant is accepted
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def start_task(request):
    if request.method == 'POST':

        #returns 404 if no such task exists
        task = get_object_or_404(Task, pk=request.data["task_id"])

        # if task is not currently open, return an error
        if task.status != Task.OPEN:
            return Response({"error":"Task is not open and cannot be started"}, status=status.HTTP_400_BAD_REQUEST)
        #ensures correct user is starting the task
        if task.owner.id != request.user.id:
            return Response({"error":"Current User does not own this task"}, status=status.HTTP_400_BAD_REQUEST)

        #makes a serializer from the existing task
        old_serializer = TaskPostSerializer(task)

        #creates new serializer data based on old task with a new status
        new_data = old_serializer.data
        new_data["status"] = Task.IN_PROGRESS

        serializer = TaskPostSerializer(task,data=new_data)
        if serializer.is_valid():
            serializer.save()
            print(serializer.data)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Sets the status of task to "completed"
# Called when the Poster judges that the task is done
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def complete_task(request):
    if request.method == 'POST':

        #returns 404 if no such task exists
        task = get_object_or_404(Task, pk=request.data["task_id"])

        # if task is not currently in progress, return an error
        if task.status != Task.IN_PROGRESS:
            return Response({"error":"Task is not In Progress and cannot be Completed"}, status=status.HTTP_400_BAD_REQUEST)
        #ensures correct user is starting the task
        if task.owner.id != request.user.id:
            return Response({"error":"Current User does not own this task"}, status=status.HTTP_400_BAD_REQUEST)

        #makes a serializer from the existing task
        old_serializer = TaskPostSerializer(task)

        #creates new serializer data based on old task with a new status
        new_data = old_serializer.data
        new_data["status"] = Task.COMPLETE

        serializer = TaskPostSerializer(task,data=new_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)


        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
        

# View all applicants of a task
@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def view_applicants(request, task_id):
    if request.method == 'GET':
        
        # Return 404 if doesn't doesn't exists
        task = get_object_or_404(Task, pk=task_id)
        
        # Get the profile of requester and profile of task owner
        requester = request.user.profile
        owner = Task.objects.get(pk=task_id).owner
        
        # Check requester is the task owner
        if not requester == owner:
            return Response({"error":"Cannot view applicants as not task owner"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get the Profile Tasks for the task, where the status is "applied"
        profile_tasks = ProfileTask.objects.filter(task=task_id, status=ProfileTask.APPLIED)
        
        # Use applicant serializer to just serializer the profile attribute from ProfileTask
        serializer = ApplicantSerializer(profile_tasks, many=True)
        
        # Return the list of Profiles that have applied for the task
        return Response(serializer.data, status=status.HTTP_200_OK)
        

# TODO Provide Helper object in response, not just ID
# Accept an applicant and start the task 

@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def accept_applicant(request, task_id):

    task = get_object_or_404(Task, pk=task_id)
    applicant = get_object_or_404(Profile, pk=request.data["profile"])
    print(applicant)
    
    #ensures correct user is accepting applicant
    if task.owner.id != request.user.id:
        return Response({"error":"Current User does not own this task"}, status=status.HTTP_400_BAD_REQUEST)

    #Check the task is Open and does not have a helper
    if (task.status != Task.OPEN or task.helper != None):
        return Response({"error":"Task must be open, and have no helper assigned"}, status=status.HTTP_400_BAD_REQUEST)

    #Check that the helper has submitted an application for the task
    if ((ProfileTask.objects.filter(profile=applicant, task=task).count()<1) or
        (ProfileTask.objects.filter(profile=applicant, task=task)[0].status != ProfileTask.APPLIED)) :
        return Response({"error":"Profile must have applied for task to be accepted"}, status=status.HTTP_400_BAD_REQUEST)


    #makes a serializer from the existing task
    old_serializer = TaskPostSerializer(task)

    new_data = old_serializer.data
    # change task status
    new_data["status"] = Task.IN_PROGRESS
    
    profile_serializer = ProfileSerializer(applicant)
    
    new_data["helper"] = applicant.pk
    

    #creates new serializer data based on old task with a new status
    serializer = TaskPostSerializer(task, data=new_data)
    
    if serializer.is_valid():
        serializer.save()

        #update the status of the profiletask
        profileTask = ProfileTask.objects.filter(profile=applicant, task=task)[0]
        profileTask.status = ProfileTask.ASSIGNED
        profileTask.save()


        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
