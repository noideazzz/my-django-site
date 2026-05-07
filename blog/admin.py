from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Post
from .models import CourseMaterial, DownloadRecord

admin.site.register(Post)


@admin.register(CourseMaterial)
class CourseMaterialAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'chapter', 'file_type', 'get_file_size_display', 'download_count', 'is_public',
                    'upload_time']
    list_filter = ['course', 'file_type', 'is_public', 'upload_time']
    search_fields = ['title', 'description']
    readonly_fields = ['file_size', 'download_count', 'upload_time', 'get_file_size_display']

    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'description', 'course', 'chapter')
        }),
        ('文件', {
            'fields': ('file', 'file_type', 'get_file_size_display', 'file_size')
        }),
        ('权限设置', {
            'fields': ('is_public', 'require_login')
        }),
        ('统计信息', {
            'fields': ('download_count', 'upload_time', 'uploader'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        """自动记录上传者"""
        if not change:  # 新建时
            obj.uploader = request.user
        super().save_model(request, obj, form, change)


@admin.register(DownloadRecord)
class DownloadRecordAdmin(admin.ModelAdmin):
    list_display = ['user', 'material', 'download_time', 'ip_address']
    list_filter = ['download_time']
    search_fields = ['user__username', 'material__title']
    readonly_fields = ['user', 'material', 'download_time', 'ip_address']