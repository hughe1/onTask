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

from jobs.models import *
from jobs.serializers import *


class ProfileList(generics.ListAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileUserSerializer


class ProfileDetail(generics.RetrieveAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileUserSerializer


class ProfileTaskList(generics.ListAPIView):
    queryset = ProfileTask.objects.all()
    serializer_class = ProfileTaskSerializer


class ProfileTaskDetail(generics.RetrieveAPIView):
    queryset = ProfileTask.objects.all()
    serializer_class = ProfileTaskSerializer


class TaskList(generics.ListAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskGetSerializer


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
        serializer = ProfileTaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if not serializer.is_valid():
            return Response({"error":"Serializer not valid"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)


# Written so that any task can be discarded, regardless of status. 
# May need to be updated if we want 'in progress' tasks to not be discarded. 
@api_view(['POST'])
#@permission_classes((IsAuthenticated, ))
def discard_task(request):
    if request.method == 'POST':

        #checks to see if ProfileTask already exists
        profile = request.data['profile']
        task = request.data['task']

        # set status of profiletask to 'discarded'
        request.data['status']=ProfileTask.DISCARDED

        #if a profileTask already exists for the given profile and task, get it
        # otherwise, create a new profiletask
        if (ProfileTask.objects.filter(profile=profile, task=task).count()>0):

            profileTask = ProfileTask.objects.filter(profile=profile, task=task)[0]
            serializer = ProfileTaskSerializer(profileTask, data=request.data)
        else:
            serializer = ProfileTaskSerializer(data=request.data)

        #save the serializer
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)
        
# Permission classes disabled for testing purposes. Need to re-enable 
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def apply_task(request):
    if request.method == 'POST':

        #returns 404 if no such ProfileTask exists
        profile_task = get_object_or_404(ProfileTask, pk=request.data["profiletask_id"])

        # if task has already been assigned or rejected, return an error
        if profile_task.status =='R' or profile_task.status == "AS":
            return Response({"error":"task has already been assigned/rejected"}, status=status.HTTP_400_BAD_REQUEST)

        #set status to 'applied'
        request.data["status"] = "AP"

        #set compulsory fields in the serializer
        request.data["task"] = profile_task.task.id
        request.data["profile"] = profile_task.profile.id

        serializer = ProfileTaskSerializer(profile_task,data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def create_profile(request):
    if request.method == 'POST':

        #make the user
        user_serializer = UserSerializer(data=request.data)
        if not user_serializer.is_valid():
            return Response(user_serializer.data, status=status.HTTP_400_BAD_REQUEST)
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
            return Response(profile_serializer.data, status=status.HTTP_400_BAD_REQUEST)
        profile_serializer.save()

        return Response(user_serializer.data, status=status.HTTP_201_CREATED)        

@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def create_task(request):
    if request.method == 'POST':

        request.data["owner"] = request.user.profile.id
        task_serializer = TaskPostSerializer(data=request.data)
        if not task_serializer.is_valid():
            return Response(task_serializer.data, status=status.HTTP_400_BAD_REQUEST)
        task_serializer.save()
        return Response(task_serializer.data, status=status.HTTP_201_CREATED)    
        
        
        
        
        
        
        
        
        
