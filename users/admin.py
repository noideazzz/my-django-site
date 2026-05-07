from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserRegistrationLog, IPRegistrationRestriction


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """自定义用户管理后台"""
    list_display = ['username', 'email', 'is_staff', 'is_admin_user', 'is_active', 'created_at']
    list_filter = ['is_staff', 'is_admin_user', 'is_active', 'created_at']
    search_fields = ['username', 'email']
    ordering = ['-created_at']

    # 编辑用户时显示的字段
    fieldsets = UserAdmin.fieldsets + (
        ('附加信息', {'fields': ('phone', 'nickname', 'avatar', 'major', 'grade', 'bio', 'is_admin_user')}),
    )

    # 添加用户时显示的字段
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('附加信息', {'fields': ('email', 'phone', 'is_admin_user')}),
    )


@admin.register(UserRegistrationLog)
class UserRegistrationLogAdmin(admin.ModelAdmin):
    """用户注册日志管理后台"""
    list_display = ['action', 'operator', 'target_username', 'target_email', 'ip_address', 'created_at']
    list_filter = ['action', 'created_at']
    search_fields = ['operator__username', 'target_username', 'target_email', 'ip_address']
    readonly_fields = ['action', 'operator', 'target_user', 'target_username', 'target_email', 
                       'ip_address', 'user_agent', 'request_data', 'error_message', 'created_at']
    ordering = ['-created_at']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(IPRegistrationRestriction)
class IPRegistrationRestrictionAdmin(admin.ModelAdmin):
    """IP注册限制管理后台"""
    list_display = ['ip_address', 'attempt_count', 'is_blocked', 'blocked_until', 'last_attempt_at']
    list_filter = ['is_blocked', 'last_attempt_at']
    search_fields = ['ip_address']
    ordering = ['-last_attempt_at']