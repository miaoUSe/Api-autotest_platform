from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
# core/views.py
from django.contrib.auth import authenticate, login, logout
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
import json
import logging

from .models import (
    Project, Environment, ApiCategory, ApiInterface,
    TestCase, TestSuite, TestSuiteCase, TestExecution, TestReport
)
from .serializers import (
    ProjectSerializer, EnvironmentSerializer, ApiCategorySerializer,
    ApiInterfaceSerializer, TestCaseSerializer, TestSuiteSerializer,
    TestSuiteCaseSerializer, TestExecutionSerializer, TestReportSerializer,
    UserRegisterSerializer, UserLoginSerializer
)
from .executor import TestRunner
from .har_importer import HARImporter, analyze_har_file
from .permissions import get_accessible_resources, check_resource_permission
from .permissions import ProjectPermissionMixin

logger = logging.getLogger(__name__)



class RegisterView(APIView):
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            login(request, user)
            return Response({"message": "注册成功", "username": user.username}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return Response({"message": "登录成功", "username": user.username}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "用户名或密码错误"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({"message": "退出成功"}, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name='dispatch')
class ProjectViewSet(ProjectPermissionMixin, viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # 自动将当前登录用户设为创建者
        serializer.save(creator=self.request.user)


class TestCaseViewSet(viewsets.ModelViewSet):
    queryset = TestCase.objects.all()
    serializer_class = TestCaseSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    def get_queryset(self):
        # 允许通过 project_id 过滤用例
        queryset = super().get_queryset()
        project_id = self.request.query_params.get('project_id')
        if project_id is not None:
            queryset = queryset.filter(project_id=project_id)
        return queryset


from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .executor import send_request, run_assertions 

class RunTestCaseView(APIView):
    permission_classes = [IsAuthenticated] 

    def post(self, request):
        data = request.data
        # 提取 method, path, headers, body, config_elements, base_url
        method = data.get('method', 'GET')
        path = data.get('path', '')
        headers = data.get('headers', {})
        body = data.get('body', {})
        config_elements = data.get('config_elements', [])
        base_url = data.get('base_url', '')
        
        # 构造完整 URL
        full_url = base_url.rstrip('/') + path
        
        # 1. 执行请求，禁用代理以避免连接问题
        request_result = send_request(
            method=method,
            url=full_url,
            headers=headers,
            body=body,
            proxies={'http': None, 'https': None}  # 禁用代理
        )
        
        # 2. 运行断言
        assertion_results = []
        if request_result.get('success'):
            assertion_results = run_assertions(request_result, config_elements)

        # 3. 构造返回结果
        response_data = {
            "request_info": {
                "method": method,
                "url": full_url,
                "headers": headers,
                "body": body
            },
            "response_info": request_result,
            "assertion_results": assertion_results,
            "overall_pass": all(r.get('passed', False) for r in assertion_results) if assertion_results else True
        }
        
        return Response(response_data, status=status.HTTP_200_OK)


class BatchRunView(APIView):
    permission_classes = [IsAuthenticated] 

    def post(self, request):
        # 获取请求数据
        data = request.data
        project_id = data.get('project_id')
        testcase_ids = data.get('testcase_ids', [])
        base_url = data.get('base_url', '')
        
        # 校验参数
        if not project_id or not testcase_ids or not base_url:
            return Response(
                {"error": "缺少必要参数: project_id, testcase_ids, base_url"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 检查项目是否存在
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response(
                {"error": "指定的项目不存在"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 实例化测试运行器
        runner = TestRunner(project_id=project_id, executor=request.user)
        
        # 执行测试并生成报告
        try:
            report = runner.execute(testcase_ids=testcase_ids, base_url=base_url)
            return Response(
                {"report_id": report.id, "message": "批量执行完成"}, 
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": f"执行过程中发生错误: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TestReportViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TestReport.objects.all()
    serializer_class = TestReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # 允许通过 project_id 过滤报告
        queryset = super().get_queryset()
        project_id = self.request.query_params.get('project_id')
        if project_id is not None:
            queryset = queryset.filter(project_id=project_id)
        return queryset


# 环境管理
class EnvironmentViewSet(ProjectPermissionMixin, viewsets.ModelViewSet):
    serializer_class = EnvironmentSerializer
    permission_classes = [IsAuthenticated]
    queryset = Environment.objects.all()

    def get_queryset(self):
        queryset = Environment.objects.all()
        project_id = self.request.query_params.get('project_id')
        if project_id is not None:
            queryset = queryset.filter(project_id=project_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save()


# 接口分类管理
class ApiCategoryViewSet(ProjectPermissionMixin, viewsets.ModelViewSet):
    serializer_class = ApiCategorySerializer
    permission_classes = [IsAuthenticated]
    queryset = ApiCategory.objects.all()

    def get_queryset(self):
        queryset = ApiCategory.objects.all()
        project_id = self.request.query_params.get('project_id')
        if project_id is not None:
            queryset = queryset.filter(project_id=project_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save()


# 接口管理
class ApiInterfaceViewSet(ProjectPermissionMixin, viewsets.ModelViewSet):
    serializer_class = ApiInterfaceSerializer
    permission_classes = [IsAuthenticated]
    queryset = ApiInterface.objects.all()

    def get_queryset(self):
        queryset = ApiInterface.objects.all()
        project_id = self.request.query_params.get('project_id')
        category_id = self.request.query_params.get('category_id')

        if project_id is not None:
            queryset = queryset.filter(project_id=project_id)
        if category_id is not None:
            queryset = queryset.filter(category_id=category_id)

        return queryset

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


# HAR文件导入
class HarImportView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        try:
            # 获取参数
            project_id = request.data.get('project_id')
            category_id = request.data.get('category_id')
            category_name = request.data.get('category_name', 'HAR导入')
            create_test_cases = request.data.get('create_test_cases', False)
            har_file = request.FILES.get('har_file')

            if not project_id:
                return Response(
                    {'error': '缺少项目ID'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if not har_file:
                return Response(
                    {'error': '缺少HAR文件'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 验证文件类型
            if not har_file.name.endswith('.har'):
                return Response(
                    {'error': '文件类型错误，请上传.har文件'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 读取HAR文件内容
            try:
                har_content = har_file.read().decode('utf-8')
                har_data = json.loads(har_content)
            except json.JSONDecodeError:
                return Response(
                    {'error': 'HAR文件格式错误，无法解析JSON'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            except Exception as e:
                return Response(
                    {'error': f'读取文件失败: {str(e)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 先分析HAR文件
            analysis = analyze_har_file(har_data)
            if not analysis['success']:
                return Response(
                    {'error': f'HAR文件分析失败: {analysis["error"]}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 创建导入器并执行导入
            importer = HARImporter(
                project_id=int(project_id),
                user=request.user,
                category_id=int(category_id) if category_id else None
            )

            result = importer.import_from_har_data(
                har_data,
                create_test_cases=create_test_cases,
                category_name=category_name
            )

            if result['success']:
                response_data = {
                    'success': True,
                    'message': 'HAR文件导入成功',
                    'analysis': analysis['stats'],
                    'import_result': result
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {'error': result['error']},
                    status=status.HTTP_400_BAD_REQUEST
                )

        except Exception as e:
            logger.error(f"HAR导入过程中发生错误: {str(e)}")
            return Response(
                {'error': f'导入过程中发生错误: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# HAR文件分析（不导入，仅分析）
class HarAnalyzeView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        try:
            har_file = request.FILES.get('har_file')

            if not har_file:
                return Response(
                    {'error': '缺少HAR文件'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 验证文件类型
            if not har_file.name.endswith('.har'):
                return Response(
                    {'error': '文件类型错误，请上传.har文件'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 读取和分析HAR文件
            har_content = har_file.read().decode('utf-8')
            har_data = json.loads(har_content)

            analysis = analyze_har_file(har_data)

            if analysis['success']:
                return Response({
                    'success': True,
                    'analysis': analysis['stats']
                }, status=status.HTTP_200_OK)
            else:
                return Response(
                    {'error': analysis['error']},
                    status=status.HTTP_400_BAD_REQUEST
                )

        except json.JSONDecodeError:
            return Response(
                {'error': 'HAR文件格式错误，无法解析JSON'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"HAR分析过程中发生错误: {str(e)}")
            return Response(
                {'error': f'分析过程中发生错误: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# 测试集管理
class TestSuiteViewSet(viewsets.ModelViewSet):
    serializer_class = TestSuiteSerializer
    permission_classes = [IsAuthenticated]
    queryset = TestSuite.objects.all()

    def get_queryset(self):
        queryset = TestSuite.objects.all()
        project_id = self.request.query_params.get('project_id')
        if project_id is not None:
            queryset = queryset.filter(project_id=project_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


# 测试集用例管理
class TestSuiteCaseViewSet(viewsets.ModelViewSet):
    serializer_class = TestSuiteCaseSerializer
    permission_classes = [IsAuthenticated]
    queryset = TestSuiteCase.objects.all()

    def get_queryset(self):
        queryset = TestSuiteCase.objects.all()
        test_suite_id = self.request.query_params.get('test_suite_id')
        if test_suite_id is not None:
            queryset = queryset.filter(test_suite_id=test_suite_id)
        return queryset