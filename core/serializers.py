# core/serializers.py
from django.contrib.auth.models import User
from rest_framework import serializers

from core.models import Project
from .models import TestCase

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ('username', 'password', 'email')
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

class ProjectSerializer(serializers.ModelSerializer):
    creator_name = serializers.ReadOnlyField(source='creator.username')

    class Meta:
        model = Project
        fields = ('id', 'name', 'description', 'creator_name', 'created_at', 'updated_at')
        read_only_fields = ('id', 'creator_name', 'created_at', 'updated_at')

class TestCaseSerializer(serializers.ModelSerializer):
    creator_name = serializers.ReadOnlyField(source='creator.username')
    project_name = serializers.ReadOnlyField(source='project.name')

    class Meta:
        model = TestCase
        fields = (
            'id', 'project', 'project_name', 'name', 'method', 'path',
            'headers', 'body', 'config_elements',
            'creator_name', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'creator_name', 'project_name', 'created_at', 'updated_at')


