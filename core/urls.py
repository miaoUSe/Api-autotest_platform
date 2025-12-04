# core/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import api_debug_views
from . import project_views

# 1. 创建并注册 ViewSet
router = DefaultRouter()
router.register(r'projects', views.ProjectViewSet)
router.register(r'testcases', views.TestCaseViewSet)
router.register(r'reports', views.TestReportViewSet)
router.register(r'environments', views.EnvironmentViewSet)
router.register(r'api-categories', views.ApiCategoryViewSet)
router.register(r'api-interfaces', views.ApiInterfaceViewSet)
router.register(r'test-suites', views.TestSuiteViewSet)
router.register(r'test-suite-cases', views.TestSuiteCaseViewSet)

# 2. 定义 urlpatterns
urlpatterns = [
    # 用户认证
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),

    # 测试执行
    path('run_testcase/', views.RunTestCaseView.as_view(), name='run_testcase'),
    path('batch_run/', views.BatchRunView.as_view(), name='batch_run'),

    # HAR文件导入
    path('har/import/', views.HarImportView.as_view(), name='har_import'),
    path('har/analyze/', views.HarAnalyzeView.as_view(), name='har_analyze'),

    # 接口调试和增强测试执行
    path('debug/api/', api_debug_views.ApiDebugView.as_view(), name='api_debug'),
    path('testcase/enhanced/', api_debug_views.RunTestCaseEnhancedView.as_view(), name='run_testcase_enhanced'),
    path('testsuite/run/', api_debug_views.RunTestSuiteView.as_view(), name='run_testsuite'),
    path('environment/validate/', api_debug_views.ValidateEnvironmentVariablesView.as_view(), name='validate_environment'),
    path('interface/test/', api_debug_views.RunApiInterfaceTestView.as_view(), name='run_interface_test'),

    # 项目管理和权限
    path('projects/<int:project_id>/members/', project_views.ProjectMemberView.as_view(), name='project_members'),
    path('projects/<int:project_id>/stats/', project_views.ProjectStatsView.as_view(), name='project_stats'),
    path('projects/<int:project_id>/permissions/', project_views.ProjectPermissionView.as_view(), name='project_permissions'),
    path('users/projects/', project_views.UserProjectsView.as_view(), name='user_projects'),
    path('users/search/', project_views.SearchUsersView.as_view(), name='search_users'),

    # 包含 router 生成的路由
    path('', include(router.urls)),
]