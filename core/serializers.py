# core/serializers.py
from django.contrib.auth.models import User
from rest_framework import serializers

from .models import (
    Project, Environment, ApiCategory, ApiInterface,
    TestCase, TestSuite, TestSuiteCase, TestExecution, TestReport
)

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
    members_count = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ('id', 'name', 'description', 'creator', 'creator_name', 'members',
                 'members_count', 'status', 'created_at', 'updated_at')
        read_only_fields = ('id', 'creator_name', 'created_at', 'updated_at')

    def get_members_count(self, obj):
        return obj.members.count()


class EnvironmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Environment
        fields = ('id', 'project', 'name', 'base_url', 'variables', 'headers',
                 'is_default', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class ApiCategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = ApiCategory
        fields = ('id', 'project', 'name', 'description', 'parent', 'children',
                 'sort_order', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_children(self, obj):
        children = ApiCategory.objects.filter(parent=obj).order_by('sort_order')
        return ApiCategorySerializer(children, many=True).data


class ApiInterfaceSerializer(serializers.ModelSerializer):
    creator_name = serializers.ReadOnlyField(source='creator.username')
    category_name = serializers.ReadOnlyField(source='category.name')

    class Meta:
        model = ApiInterface
        fields = ('id', 'project', 'category', 'category_name', 'name', 'description',
                 'method', 'path', 'headers', 'params', 'body', 'response_schema',
                 'examples', 'tags', 'status', 'creator', 'creator_name',
                 'updated_by', 'created_at', 'updated_at')
        read_only_fields = ('id', 'creator_name', 'created_at', 'updated_at')


class TestCaseSerializer(serializers.ModelSerializer):
    creator_name = serializers.ReadOnlyField(source='creator.username')
    project_name = serializers.ReadOnlyField(source='project.name')
    api_interface_name = serializers.ReadOnlyField(source='api_interface.name')

    class Meta:
        model = TestCase
        fields = (
            'id', 'project', 'project_name', 'api_interface', 'api_interface_name',
            'name', 'description', 'method', 'path', 'headers', 'params', 'body',
            'assertions', 'setup_script', 'teardown_script', 'status', 'sort_order',
            'creator', 'creator_name', 'updated_by', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'creator_name', 'project_name', 'api_interface_name',
                           'created_at', 'updated_at')


class TestSuiteSerializer(serializers.ModelSerializer):
    creator_name = serializers.ReadOnlyField(source='creator.username')
    test_cases_info = serializers.SerializerMethodField()

    class Meta:
        model = TestSuite
        fields = ('id', 'project', 'name', 'description', 'test_cases', 'test_cases_info',
                 'config', 'creator', 'creator_name', 'updated_by', 'created_at', 'updated_at')
        read_only_fields = ('id', 'creator_name', 'test_cases_info', 'created_at', 'updated_at')

    def get_test_cases_info(self, obj):
        """获取测试用例的详细信息"""
        suite_cases = TestSuiteCase.objects.filter(test_suite=obj).select_related('test_case')
        return [
            {
                'id': tc.test_case.id,
                'name': tc.test_case.name,
                'sort_order': tc.sort_order,
                'is_enabled': tc.is_enabled
            }
            for tc in suite_cases
        ]


class TestSuiteCaseSerializer(serializers.ModelSerializer):
    test_case_name = serializers.ReadOnlyField(source='test_case.name')

    class Meta:
        model = TestSuiteCase
        fields = ('id', 'test_suite', 'test_case', 'test_case_name',
                 'sort_order', 'is_enabled')
        read_only_fields = ('id', 'test_case_name')


class TestExecutionSerializer(serializers.ModelSerializer):
    executor_name = serializers.ReadOnlyField(source='executor.username')
    project_name = serializers.ReadOnlyField(source='project.name')
    test_suite_name = serializers.ReadOnlyField(source='test_suite.name')
    test_case_name = serializers.ReadOnlyField(source='test_case.name')
    environment_name = serializers.ReadOnlyField(source='environment.name')

    class Meta:
        model = TestExecution
        fields = ('id', 'project', 'project_name', 'test_suite', 'test_suite_name',
                 'test_case', 'test_case_name', 'environment', 'environment_name',
                 'status', 'start_time', 'end_time', 'duration', 'request_data',
                 'response_data', 'assertion_results', 'error_message', 'executor',
                 'executor_name', 'created_at')
        read_only_fields = ('id', 'executor_name', 'project_name', 'test_suite_name',
                           'test_case_name', 'environment_name', 'created_at')


class TestReportSerializer(serializers.ModelSerializer):
    executor_name = serializers.ReadOnlyField(source='executor.username')
    project_name = serializers.ReadOnlyField(source='project.name')
    environment_name = serializers.ReadOnlyField(source='environment.name')
    pass_rate = serializers.ReadOnlyField()

    class Meta:
        model = TestReport
        fields = (
            'id', 'project', 'project_name', 'execution', 'name', 'environment',
            'environment_name', 'total_cases', 'passed_cases', 'failed_cases',
            'error_cases', 'skipped_cases', 'duration', 'pass_rate', 'summary',
            'details', 'executor', 'executor_name', 'created_at'
        )
        read_only_fields = (
            'id', 'executor_name', 'project_name', 'environment_name',
            'pass_rate', 'created_at'
        )
