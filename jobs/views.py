from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from jobs.models import *
from jobs.serializers import *


class ProfileList(generics.ListAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer


class ProfileDetail(generics.RetrieveAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer


class TaskList(generics.ListAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


class TaskDetail(generics.RetrieveAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


# UPDATE from swipe_task
# This accepts task and user through POST data instead of through URL
# TODO - Get or Create logic for if UserTask has already been created
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def shortlist_task(request):
    if request.method == 'POST':
        serializer = UserTaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)
        
# This accepts user  and profileinfo through POST data instead of through URL
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
        
        
        
        
        
        
        
        
        
