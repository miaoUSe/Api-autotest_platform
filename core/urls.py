# core/urls.py
from django.urls import path, include  # 确保引入了 include
from rest_framework.routers import DefaultRouter
from . import views

# 1. 创建并注册 ViewSet
router = DefaultRouter()
router.register(r'projects', views.ProjectViewSet)
router.register(r'testcases', views.TestCaseViewSet)  # 新增

# 2. 定义 urlpatterns
urlpatterns = [
    # 阶段一的路由（path 模式）
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('run_testcase/', views.RunTestCaseView.as_view(), name='run_testcase'), # 新增
    # path('about/', views.AboutView.as_view(), name='about')

    # 3. 关键步骤：包含 router 生成的路由（include 模式）
    # router.urls 会生成 /projects/ 和 /testcases/ 等路由
    path('', include(router.urls)),
]

