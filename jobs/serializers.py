from rest_framework import serializers
from jobs.models import *
from django.contrib.auth.models import User

#class UserSerializer(serializers.ModelSerializer):

 #   class Meta:
 #       model = User
 #       fields = ('id', 'username')

class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ('user','location', 'description','photo','date_created')

class TaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = "__all__"
