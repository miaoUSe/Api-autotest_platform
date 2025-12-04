from django.db import models

# Create your models here.
# core/models.py

from django.db import models
from django.contrib.auth.models import User

class Project(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="项目名称")
    description = models.TextField(blank=True, null=True, verbose_name="项目描述")
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="创建者")
    members = models.ManyToManyField(User, related_name='project_members', blank=True, verbose_name="项目成员")
    status = models.CharField(max_length=20, choices=[
        ('active', '活跃'),
        ('archived', '已归档'),
    ], default='active', verbose_name="项目状态")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "项目管理"
        verbose_name_plural = "项目管理"
        ordering = ['-created_at']
    def __str__(self):
        return self.name


class Environment(models.Model):
    """环境管理"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="所属项目")
    name = models.CharField(max_length=50, verbose_name="环境名称")
    base_url = models.URLField(verbose_name="基础URL")
    variables = models.JSONField(default=dict, blank=True, verbose_name="环境变量")
    headers = models.JSONField(default=dict, blank=True, verbose_name="全局请求头")
    is_default = models.BooleanField(default=False, verbose_name="是否默认环境")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "环境管理"
        verbose_name_plural = "环境管理"
        unique_together = ('project', 'name')
        ordering = ['-created_at']
    def __str__(self):
        return f"{self.project.name} - {self.name}"


class ApiCategory(models.Model):
    """接口分类"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="所属项目")
    name = models.CharField(max_length=100, verbose_name="分类名称")
    description = models.TextField(blank=True, null=True, verbose_name="分类描述")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, verbose_name="父分类")
    sort_order = models.IntegerField(default=0, verbose_name="排序")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "接口分类"
        verbose_name_plural = "接口分类"
        unique_together = ('project', 'name', 'parent')
        ordering = ['sort_order', 'created_at']
    def __str__(self):
        return self.name


class ApiInterface(models.Model):
    """接口定义"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="所属项目")
    category = models.ForeignKey(ApiCategory, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="接口分类")
    name = models.CharField(max_length=200, verbose_name="接口名称")
    description = models.TextField(blank=True, null=True, verbose_name="接口描述")
    method = models.CharField(max_length=10, choices=[
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('DELETE', 'DELETE'),
        ('PATCH', 'PATCH'),
        ('HEAD', 'HEAD'),
        ('OPTIONS', 'OPTIONS'),
    ], verbose_name="请求方法")
    path = models.CharField(max_length=500, verbose_name="接口路径")
    headers = models.JSONField(default=dict, blank=True, verbose_name="请求头")
    params = models.JSONField(default=dict, blank=True, verbose_name="查询参数")
    body = models.JSONField(default=dict, blank=True, verbose_name="请求体")
    response_schema = models.JSONField(default=dict, blank=True, verbose_name="响应结构")
    examples = models.JSONField(default=list, blank=True, verbose_name="请求示例")
    tags = models.JSONField(default=list, blank=True, verbose_name="标签")
    status = models.CharField(max_length=20, choices=[
        ('draft', '草稿'),
        ('active', '活跃'),
        ('deprecated', '已废弃'),
    ], default='draft', verbose_name="状态")
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="创建者")
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='updated_apis', verbose_name="更新者")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "接口管理"
        verbose_name_plural = "接口管理"
        unique_together = ('project', 'name')
        ordering = ['-created_at']
    def __str__(self):
        return self.name


class TestCase(models.Model):
    """测试用例"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="所属项目")
    api_interface = models.ForeignKey(ApiInterface, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="关联接口")
    name = models.CharField(max_length=255, verbose_name="用例名称")
    description = models.TextField(blank=True, null=True, verbose_name="用例描述")

    # 请求配置
    method = models.CharField(max_length=10, choices=[
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('DELETE', 'DELETE'),
        ('PATCH', 'PATCH'),
        ('HEAD', 'HEAD'),
        ('OPTIONS', 'OPTIONS'),
    ], default='GET', verbose_name="请求方法")
    path = models.CharField(max_length=500, verbose_name="接口路径")
    headers = models.JSONField(default=dict, blank=True, verbose_name="请求头")
    params = models.JSONField(default=dict, blank=True, verbose_name="查询参数")
    body = models.JSONField(default=dict, blank=True, verbose_name="请求体")

    # 断言配置
    assertions = models.JSONField(default=list, blank=True, verbose_name="断言配置")

    # 前后置脚本
    setup_script = models.TextField(blank=True, null=True, verbose_name="前置脚本")
    teardown_script = models.TextField(blank=True, null=True, verbose_name="后置脚本")

    # 状态和排序
    status = models.CharField(max_length=20, choices=[
        ('active', '活跃'),
        ('inactive', '非活跃'),
    ], default='active', verbose_name="状态")
    sort_order = models.IntegerField(default=0, verbose_name="排序")

    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="创建者")
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='updated_testcases', verbose_name="更新者")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "测试用例"
        verbose_name_plural = "测试用例"
        unique_together = ('project', 'name')
        ordering = ['sort_order', '-created_at']
    def __str__(self):
        return self.name


class TestSuite(models.Model):
    """测试集"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="所属项目")
    name = models.CharField(max_length=200, verbose_name="测试集名称")
    description = models.TextField(blank=True, null=True, verbose_name="测试集描述")
    test_cases = models.ManyToManyField(TestCase, through='TestSuiteCase', verbose_name="测试用例")
    config = models.JSONField(default=dict, blank=True, verbose_name="配置信息")
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="创建者")
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='updated_testsuites', verbose_name="更新者")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "测试集"
        verbose_name_plural = "测试集"
        unique_together = ('project', 'name')
        ordering = ['-created_at']
    def __str__(self):
        return self.name


class TestSuiteCase(models.Model):
    """测试集用例关联表"""
    test_suite = models.ForeignKey(TestSuite, on_delete=models.CASCADE, verbose_name="测试集")
    test_case = models.ForeignKey(TestCase, on_delete=models.CASCADE, verbose_name="测试用例")
    sort_order = models.IntegerField(default=0, verbose_name="执行顺序")
    is_enabled = models.BooleanField(default=True, verbose_name="是否启用")

    class Meta:
        verbose_name = "测试集用例"
        verbose_name_plural = "测试集用例"
        unique_together = ('test_suite', 'test_case')
        ordering = ['sort_order']
    def __str__(self):
        return f"{self.test_suite.name} - {self.test_case.name}"


class TestExecution(models.Model):
    """测试执行记录"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="所属项目")
    test_suite = models.ForeignKey(TestSuite, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="测试集")
    test_case = models.ForeignKey(TestCase, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="测试用例")
    environment = models.ForeignKey(Environment, on_delete=models.PROTECT, verbose_name="执行环境")
    status = models.CharField(max_length=20, choices=[
        ('pending', '待执行'),
        ('running', '执行中'),
        ('passed', '通过'),
        ('failed', '失败'),
        ('error', '错误'),
        ('cancelled', '已取消'),
    ], default='pending', verbose_name="执行状态")

    # 时间信息
    start_time = models.DateTimeField(null=True, blank=True, verbose_name="开始时间")
    end_time = models.DateTimeField(null=True, blank=True, verbose_name="结束时间")
    duration = models.FloatField(null=True, blank=True, verbose_name="执行时长(秒)")

    # 请求响应数据
    request_data = models.JSONField(default=dict, blank=True, verbose_name="请求数据")
    response_data = models.JSONField(default=dict, blank=True, verbose_name="响应数据")
    assertion_results = models.JSONField(default=list, blank=True, verbose_name="断言结果")
    error_message = models.TextField(blank=True, null=True, verbose_name="错误信息")

    executor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="执行者")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "测试执行记录"
        verbose_name_plural = "测试执行记录"
        ordering = ['-created_at']
    def __str__(self):
        return f"{self.project.name} - {self.status}"


class TestReport(models.Model):
    """测试报告"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="所属项目")
    execution = models.OneToOneField(TestExecution, on_delete=models.CASCADE, null=True, blank=True, verbose_name="执行记录")
    name = models.CharField(max_length=255, verbose_name="报告名称")
    environment = models.ForeignKey(Environment, on_delete=models.PROTECT, null=True, blank=True, verbose_name="执行环境")

    # 统计信息
    total_cases = models.IntegerField(default=0, verbose_name="总用例数")
    passed_cases = models.IntegerField(default=0, verbose_name="通过数")
    failed_cases = models.IntegerField(default=0, verbose_name="失败数")
    error_cases = models.IntegerField(default=0, verbose_name="错误数")
    skipped_cases = models.IntegerField(default=0, verbose_name="跳过数")
    duration = models.FloatField(default=0.0, verbose_name="总耗时(秒)")

    # 详细信息
    summary = models.JSONField(default=dict, blank=True, verbose_name="执行摘要")
    details = models.JSONField(default=list, blank=True, verbose_name="详细结果")

    executor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="执行者")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="生成时间")

    class Meta:
        verbose_name = "测试报告"
        verbose_name_plural = "测试报告"
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def pass_rate(self):
        """通过率"""
        if self.total_cases == 0:
            return 0
        return round((self.passed_cases / self.total_cases) * 100, 2)
