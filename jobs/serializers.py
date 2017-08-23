from rest_framework import serializers
from jobs.models import *
from django.contrib.auth.models import User

#class UserSerializer(serializers.ModelSerializer):

 #   class Meta:
 #       model = User
 #       fields = ('id', 'username')


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = "__all__"

class ProfileSerializer(serializers.ModelSerializer):
    
    user = UserSerializer()
    
    class Meta:
        model = Profile
        # fields = ('user','location', 'description','photo','date_created')
        fields = "__all__"
        
class TaskSerializer(serializers.ModelSerializer):
    
    owner = ProfileSerializer()

    class Meta:
        model = Task
        fields = "__all__"

class ProfileTaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProfileTask
        fields = "__all__"
