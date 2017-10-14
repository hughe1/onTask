"""job_bilby Serializers for the Job Application

This file belongs to the back end source code for team 'job-bilby' for the
University of Melbourne subject SWEN90014 Masters Software Engineering Project.
The project is a mobile-first web application for sharing tasks.
The back-end is based on the REST Framework for Django.

Client: Paul Ashkar (Capgemini)                 paul.ashkar@capgemini.com
Supervisor: Rachel Burrows                      rachel.burrows@unimelb.edu.au
Team:
Annie Zhou:                                     azhou@student.unimelb.edu.au
David Barrel:                                   dbarrell@student.unimelb.edu.au
Grace Johnson:                                  gjohnson1@student.unimelb.edu.au
Hugh Edwards:                                   hughe@student.unimelb.edu.au
Matt Perrot:                                    mperrott@student.unimelb.edu.au
View our 'Project Overview' document on Confluence for more information about the project.
Date project started: 6/8/2017
Date project completed: 15/10/2017
"""
import base64, uuid
from rest_framework import serializers
from jobs.models import *
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from job_bilby import settings


class SkillSerializer(serializers.ModelSerializer):
    """ Serializer for Skill model"""

    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        if str(obj.image) is not '':
            return settings.BASE_URL + obj.image.url
        else:
            return None

    class Meta:
        model = Skill
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    """ Serializer for User model"""
    class Meta:
        model = User

        # Password excluded for security purposes
        exclude = ('password',)


class ProfileSkillSerializer(serializers.ModelSerializer):
    """ Serializer for ProfileSkill Model """

    class Meta:
        model = ProfileSkill
        fields = "__all__"

class ProfileSkillGetSerializer(serializers.ModelSerializer):
    """ Serializer for ProfileSkill Model """
    skill = SkillSerializer()

    class Meta:
        model = ProfileSkill
        fields = "__all__"


class ProfileSerializer(serializers.ModelSerializer):
    """ Serializer for Profile model"""

    photo = serializers.SerializerMethodField()

    def get_photo(self, obj):
        if str(obj.photo) is not '':
            return settings.BASE_URL + obj.photo.url
        else:
            return None

    class Meta:
        model = Profile
        fields = "__all__"


class Base64ImageField(serializers.ImageField):
    """Custom image field - handles base 64 encoded images"""
    def to_internal_value(self, data):
        """ Encodes an image represented by data to be stored """
        if isinstance(data, str) and data.startswith('data:image'):
            # Found image is encoded, and must be decoded
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1] # Extract file extension
            id = uuid.uuid4()
            data = ContentFile(base64.b64decode(imgstr), name = id.urn[9:] + '.' + ext)
        return super(Base64ImageField, self).to_internal_value(data)


class ProfileUserSerializer(serializers.ModelSerializer):
    """ Serializer for ProfileUser model"""
    user = UserSerializer()
    photo = Base64ImageField()

    class Meta:
        model = Profile
        fields = "__all__"


class ProfileUserGetSerializer(serializers.ModelSerializer):
    """ Serializer for ProfileUser model"""
    user = UserSerializer()
    photo = Base64ImageField()
    profile_skills = ProfileSkillGetSerializer(many=True, read_only=True)

    class Meta:
        model = Profile
        fields = "__all__"


class TaskGetSerializer(serializers.ModelSerializer):
    """ Serializer, used when GET-ing a task
        Contains all Task data, along with data for its Poster (owner)
        and Helper.
    """
    owner = ProfileUserSerializer()
    helper = ProfileUserSerializer(required=False)
    skills = SkillSerializer(many=True)

    class Meta:
        model = Task
        fields = "__all__"


class TaskPostSerializer(serializers.ModelSerializer):
    """ Serializer, used when POST-ing a task
        Contains all Task data, without extra data (ie poster/helper data)
    """
    class Meta:
        model = Task
        fields = "__all__"


class TaskHelperSerializer(serializers.ModelSerializer):
    """ Serializer, used when setting or updating the Helper of a Task.
    """
    helper = ProfileSerializer(required=False)

    class Meta:
        model = Task
        fields = "__all__"

    def update(self, instance, validated_data):
        """ Update the TaskHelperSerializer with validated data"""
        helper_data = validated_data.pop('helper')
        helper = instance.helper

        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.offer = validated_data.get('offer', instance.offer)
        instance.location = validated_data.get('location', instance.location)
        instance.is_remote = validated_data.get('is_remote', instance.is_remote)
        instance.owner = validated_data.get('owner', instance.owner)
        instance.quote = validated_data.get('quote', instance.quote)
        instance.save()

        helper.user = helper_data.get('user', helper.user)
        helper.save()

        return instance


class ProfileTaskGetSerializer(serializers.ModelSerializer):
    """ Serializer, used when GET-ing a ProfileTask
        Contains all ProfileTask data, along with the relevant Task data
    """
    task = TaskGetSerializer()

    class Meta:
        model = ProfileTask
        fields = "__all__"


class ProfileTaskPostSerializer(serializers.ModelSerializer):
    """ Serializer, used when POST-ing a ProfileTask
        Contains all ProfileTask data
    """
    class Meta:
        model = ProfileTask
        fields = "__all__"


class ApplicantSerializer(serializers.ModelSerializer):
    """ Serializer, for Task applicants (ie ProfileUsers)
        Has all Profile data, along with custom fields
        (including answers, quote, status, etc) relevant
        to applicants.
    """
    profile = ProfileUserSerializer()
    task = TaskGetSerializer()

    class Meta:
        model = ProfileTask
        fields = ['id','profile','answer1','answer2','answer3','quote','status','task']
