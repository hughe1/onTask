from jobs.models import *
from jobs.serializers import *
from rest_framework import generics, permissions
from django.contrib.auth.models import User
from django.http import HttpResponse

#from jobs.permissions import IsOwnerOrReadOnly


#class UserList(generics.ListAPIView):
#    queryset = User.objects.all()
#    serializer_class = UserSerializer

#class UserDetail(generics.RetrieveAPIView):
#    queryset = User.objects.all()
#    serializer_class = UserSerializer

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

def swipe_task(request, profile_id, task_id):#, is_right):

	task = Task.objects.get(pk= task_id)
	profile = Profile.objects.get(pk= profile_id)

	user_task = UserTask.objects.create(profile=profile,task=task)
	user_task.save()

	
	return HttpResponse("hello")

