from django.db import models

# Create your models here.
# core/models.py

from django.db import models
from django.contrib.auth.models import User

class Project(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="项目名称")
    description = models.TextField(blank=True, null=True, verbose_name="项目描述")
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="创建者")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "项目管理"
        verbose_name_plural = "项目管理"
        ordering = ['-created_at']
    def __str__(self):
        return self.name


class TestCase(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="所属项目")
    name = models.CharField(max_length=255, verbose_name="用例名称")
    method = models.CharField(max_length=10, default='GET', verbose_name="请求方法")
    path = models.CharField(max_length=500, verbose_name="接口路径")

    # 核心 JSON 字段
    headers = models.JSONField(default=dict, blank=True, verbose_name="请求头")
    body = models.JSONField(default=dict, blank=True, verbose_name="请求体")
    config_elements = models.JSONField(default=list, blank=True, verbose_name="配置元件")

    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="创建者")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        unique_together = ('project', 'name')
        ordering = ['-created_at']