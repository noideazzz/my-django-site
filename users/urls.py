from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # 认证相关
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # 密码管理
    path('password/change/', views.password_change_view, name='password_change'),
    path('password/reset/', views.password_reset_request_view, name='password_reset_request'),
    path('password/reset/<str:token>/', views.password_reset_confirm_view, name='password_reset_confirm'),

    # 安全设置
    path('security/', views.security_settings_view, name='security_settings'),

    # API接口
    path('api/check-username/', views.check_username_api, name='check_username'),
    path('api/check-email/', views.check_email_api, name='check_email'),
# 个人中心
    path('profile/', views.profile_view, name='profile'),
    path('profile/update/', views.profile_update, name='profile_update'),
    path('profile/avatar/upload/', views.avatar_upload, name='avatar_upload'),
]