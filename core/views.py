from django.shortcuts import render

# Create your views here.
# core/views.py
from django.contrib.auth import authenticate, login, logout
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserRegisterSerializer, UserLoginSerializer
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Project
from .serializers import ProjectSerializer
from .models import TestCase
from .serializers import TestCaseSerializer



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


class ProjectViewSet(viewsets.ModelViewSet):
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
        
        # 1. 执行请求
        request_result = send_request(
            method=method,
            url=full_url,
            headers=headers,
            body=body
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

