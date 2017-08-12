from rest_framework import serializers
from jobs.models import *
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    #snippets = serializers.PrimaryKeyRelatedField(many=True, queryset=Snippet.objects.all())

    class Meta:
        model = User
        fields = ('id', 'username')