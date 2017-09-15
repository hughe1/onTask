from rest_framework import serializers
from jobs.models import *
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = "__all__"

class ProfileSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Profile
        fields = "__all__"
        
class ProfileUserSerializer(serializers.ModelSerializer):
    
    user = UserSerializer()
    
    class Meta:
        model = Profile
        fields = "__all__"
        
class TaskGetSerializer(serializers.ModelSerializer):
    
    owner = ProfileSerializer()

    class Meta:
        model = Task
        fields = "__all__"
        
class TaskPostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = "__all__"


# TODO Solve unique field error on helper.user
class TaskHelperSerializer(serializers.ModelSerializer):
    
    helper = ProfileSerializer(required=False)
    
    class Meta:
        model = Task
        fields = "__all__"
        
    def update(self, instance, validated_data):
        helper_data = validated_data.pop('helper')
        helper = instance.helper

        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.points = validated_data.get('points', instance.points)
        instance.location = validated_data.get('location', instance.location)
        instance.is_remote = validated_data.get('is_remote', instance.is_remote)
        instance.owner = validated_data.get('owner', instance.owner)
        instance.quote = validated_data.get('quote', instance.quote)
        instance.save()
        
        helper.user = helper_data.get('user', helper.user)
        helper.save()

        return instance

class ProfileTaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProfileTask
        fields = "__all__"

# To serialize ProfileTasks into just the list of Profiles
class ApplicantSerializer(serializers.ModelSerializer):
    
    profile = ProfileUserSerializer()
    
    class Meta:
        model = ProfileTask
        fields = ['profile','answer1','answer2','answer3','quote']
