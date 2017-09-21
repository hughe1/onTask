import base64, uuid
from rest_framework import serializers
from jobs.models import *
from django.contrib.auth.models import User
from django.core.files.base import ContentFile

# Custom image field - handles base 64 encoded images
class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            # base64 encoded image - decode
            format, imgstr = data.split(';base64,') # format ~= data:image/X,
            ext = format.split('/')[-1] # guess file extension
            id = uuid.uuid4()
            data = ContentFile(base64.b64decode(imgstr), name = id.urn[9:] + '.' + ext)
        return super(Base64ImageField, self).to_internal_value(data)


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        exclude = ('password',)

class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = "__all__"

class ProfileUserSerializer(serializers.ModelSerializer):

    user = UserSerializer()
    photo = Base64ImageField()

    class Meta:
        model = Profile
        fields = "__all__"

class TaskGetSerializer(serializers.ModelSerializer):

    owner = ProfileUserSerializer()
    helper = ProfileUserSerializer(required=False)

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


class ProfileTaskGetSerializer(serializers.ModelSerializer):

    task = TaskGetSerializer()

    class Meta:
        model = ProfileTask
        fields = "__all__"

class ProfileTaskPostSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProfileTask
        fields = "__all__"

# To serialize ProfileTasks into just the list of Profiles
class ApplicantSerializer(serializers.ModelSerializer):

    profile = ProfileUserSerializer()

    class Meta:
        model = ProfileTask
        fields = ['profile','answer1','answer2','answer3','quote']
