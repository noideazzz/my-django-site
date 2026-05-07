from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models
import json


class CustomUser(AbstractUser):
    """自定义用户模型"""
    email = models.EmailField(unique=True, verbose_name='邮箱')
    phone = models.CharField(max_length=20, blank=True, verbose_name='手机号')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    # 新增字段
    nickname = models.CharField(max_length=50, blank=True, verbose_name='昵称')
    avatar = models.ImageField(upload_to='avatars/', blank=True, verbose_name='头像')
    major = models.CharField(max_length=100, blank=True, verbose_name='专业')
    grade = models.CharField(max_length=20, blank=True, verbose_name='年级')
    bio = models.TextField(max_length=500, blank=True, verbose_name='个人简介')
    # 管理员权限字段
    is_admin_user = models.BooleanField(default=False, verbose_name='管理员权限')
    
    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'

    def __str__(self):
        return self.username
    
    def has_admin_permission(self):
        """检查用户是否有管理员权限（超级用户或标记为管理员）"""
        return self.is_superuser or self.is_admin_user or self.is_staff


class UserRegistrationLog(models.Model):
    """用户注册操作日志"""
    ACTION_CHOICES = [
        ('register', '注册新用户'),
        ('register_denied', '注册被拒绝'),
        ('register_failed', '注册失败'),
    ]
    
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name='操作类型')
    operator = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, 
                                  related_name='registration_operations', verbose_name='操作管理员')
    target_user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='registration_records', verbose_name='目标用户')
    target_username = models.CharField(max_length=150, blank=True, verbose_name='目标用户名')
    target_email = models.EmailField(blank=True, verbose_name='目标邮箱')
    ip_address = models.GenericIPAddressField(verbose_name='IP地址')
    user_agent = models.TextField(blank=True, verbose_name='用户代理')
    request_data = models.JSONField(default=dict, verbose_name='请求数据')
    error_message = models.TextField(blank=True, verbose_name='错误信息')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='操作时间')
    
    class Meta:
        verbose_name = '注册操作日志'
        verbose_name_plural = '注册操作日志'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_action_display()} - {self.operator} -> {self.target_username} at {self.created_at}"


class IPRegistrationRestriction(models.Model):
    """IP注册限制记录"""
    ip_address = models.GenericIPAddressField(unique=True, verbose_name='IP地址')
    attempt_count = models.PositiveIntegerField(default=0, verbose_name='尝试次数')
    last_attempt_at = models.DateTimeField(auto_now=True, verbose_name='最后尝试时间')
    is_blocked = models.BooleanField(default=False, verbose_name='是否被封禁')
    blocked_until = models.DateTimeField(null=True, blank=True, verbose_name='封禁截止时间')
    
    class Meta:
        verbose_name = 'IP注册限制'
        verbose_name_plural = 'IP注册限制'
    
    def __str__(self):
        return f"{self.ip_address} - 尝试{self.attempt_count}次"
