from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponseForbidden
from .forms import (
    RegisterForm, LoginForm, CustomPasswordChangeForm,
    PasswordResetRequestForm, SetNewPasswordForm
)
from .models import CustomUser, UserRegistrationLog, IPRegistrationRestriction
import hashlib
import time
from django.views.decorators.http import require_POST
import os
from django.conf import settings
from PIL import Image
import io
from functools import wraps
from django.utils import timezone
from datetime import timedelta
import json


# 临时存储重置令牌（生产环境建议使用数据库或Redis）
password_reset_tokens = {}


def get_client_ip(request):
    """获取客户端真实IP地址"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
    return ip


def check_ip_restriction(ip_address):
    """检查IP是否被限制注册"""
    try:
        restriction = IPRegistrationRestriction.objects.get(ip_address=ip_address)
        # 检查是否被封禁
        if restriction.is_blocked and restriction.blocked_until:
            if restriction.blocked_until > timezone.now():
                return False, f'该IP已被限制注册，请在 {restriction.blocked_until.strftime("%Y-%m-%d %H:%M")} 后再试'
            else:
                # 封禁时间已过，解除封禁
                restriction.is_blocked = False
                restriction.blocked_until = None
                restriction.attempt_count = 0
                restriction.save()
        return True, None
    except IPRegistrationRestriction.DoesNotExist:
        return True, None


def record_ip_attempt(ip_address, success=False):
    """记录IP注册尝试"""
    restriction, created = IPRegistrationRestriction.objects.get_or_create(
        ip_address=ip_address,
        defaults={'attempt_count': 0}
    )
    
    if success:
        # 注册成功，重置计数
        restriction.attempt_count = 0
        restriction.is_blocked = False
        restriction.blocked_until = None
    else:
        # 注册失败，增加计数
        restriction.attempt_count += 1
        
        # 如果失败次数过多，封禁IP
        if restriction.attempt_count >= 5:
            restriction.is_blocked = True
            restriction.blocked_until = timezone.now() + timedelta(hours=1)
    
    restriction.save()


def log_registration_action(request, action, target_user=None, target_username='', 
                            target_email='', error_message=''):
    """记录注册操作日志"""
    ip_address = get_client_ip(request)
    
    # 准备请求数据（排除敏感信息）
    request_data = {}
    if request.method == 'POST':
        for key, value in request.POST.items():
            if key not in ['password1', 'password2', 'password', 'csrfmiddlewaretoken']:
                request_data[key] = value
    
    UserRegistrationLog.objects.create(
        action=action,
        operator=request.user if request.user.is_authenticated else None,
        target_user=target_user,
        target_username=target_username,
        target_email=target_email,
        ip_address=ip_address,
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        request_data=request_data,
        error_message=error_message
    )


def admin_required(view_func):
    """自定义装饰器：要求用户必须是管理员"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, '请先登录')
            return redirect('users:login')
        
        if not request.user.has_admin_permission():
            log_registration_action(
                request, 
                'register_denied',
                error_message='非管理员用户尝试访问注册功能'
            )
            messages.error(request, '您没有权限执行此操作，该功能仅限管理员使用')
            return HttpResponseForbidden('权限不足：该功能仅限管理员使用')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def rate_limit_registration(max_attempts=3, window_seconds=300):
    """注册频率限制装饰器"""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.method == 'POST':
                ip_address = get_client_ip(request)
                
                # 检查IP限制
                allowed, error_msg = check_ip_restriction(ip_address)
                if not allowed:
                    log_registration_action(
                        request,
                        'register_denied',
                        error_message=error_msg
                    )
                    messages.error(request, error_msg)
                    return redirect('index')
                
                # 检查短时间内的注册频率
                recent_attempts = UserRegistrationLog.objects.filter(
                    ip_address=ip_address,
                    action='register',
                    created_at__gte=timezone.now() - timedelta(seconds=window_seconds)
                ).count()
                
                if recent_attempts >= max_attempts:
                    error_msg = f'注册过于频繁，请在 {window_seconds // 60} 分钟后重试'
                    log_registration_action(
                        request,
                        'register_denied',
                        error_message=error_msg
                    )
                    messages.error(request, error_msg)
                    return redirect('index')
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


@login_required
def profile_view(request):
    """个人中心页面"""
    return render(request, 'auth/profile.html', {'user': request.user})


@login_required
@require_POST
def profile_update(request):
    """更新个人信息"""
    user = request.user
    user.nickname = request.POST.get('nickname', '')
    user.major = request.POST.get('major', '')
    user.grade = request.POST.get('grade', '')
    user.bio = request.POST.get('bio', '')
    user.save()

    messages.success(request, '个人信息更新成功！')
    return redirect('users:profile')


@login_required
@require_POST
def avatar_upload(request):
    """上传并裁剪头像"""
    if 'avatar' not in request.FILES:
        return JsonResponse({'success': False, 'message': '请选择图片'})

    try:
        from PIL import Image
        import time
        import os
        from django.conf import settings

        # 获取上传的图片
        avatar_file = request.FILES['avatar']

        # 获取裁剪坐标
        x = int(request.POST.get('x', 0))
        y = int(request.POST.get('y', 0))
        width = int(request.POST.get('width', 0))
        height = int(request.POST.get('height', 0))

        # 打开图片
        image = Image.open(avatar_file)

        # 裁剪
        if width > 0 and height > 0:
            image = image.crop((x, y, x + width, y + height))

        # 调整大小为 300x300
        image = image.resize((300, 300), Image.Resampling.LANCZOS)

        # 保存路径
        avatar_dir = os.path.join(settings.MEDIA_ROOT, 'avatars')

        # 创建目录（处理已存在的情况）
        if not os.path.exists(avatar_dir):
            try:
                os.makedirs(avatar_dir)
            except FileExistsError:
                pass  # 目录已存在，忽略错误

        # 文件名：user_{id}_{timestamp}.jpg
        filename = f"user_{request.user.id}_{int(time.time())}.jpg"
        filepath = os.path.join(avatar_dir, filename)

        # 保存
        image = image.convert('RGB')
        image.save(filepath, 'JPEG', quality=90)

        # 更新用户头像URL
        request.user.avatar = f'avatars/{filename}'
        request.user.save()

        return JsonResponse({
            'success': True,
            'avatar_url': request.user.avatar.url
        })

    except Exception as e:
        import traceback
        print(f"上传头像错误: {traceback.format_exc()}")
        return JsonResponse({'success': False, 'message': str(e)})
# 临时存储重置令牌（生产环境建议使用数据库或Redis）
password_reset_tokens = {}


@admin_required
@rate_limit_registration(max_attempts=3, window_seconds=300)
def register_view(request):
    """
    用户注册视图 - 仅限管理员使用
    
    权限要求：
    1. 用户必须已登录
    2. 用户必须具有管理员权限（is_superuser, is_admin_user, 或 is_staff）
    
    安全防护：
    1. IP地址限制和封禁机制
    2. 注册频率限制（5分钟内最多3次）
    3. 操作日志记录
    """
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                
                # 记录成功注册日志
                log_registration_action(
                    request,
                    'register',
                    target_user=user,
                    target_username=user.username,
                    target_email=user.email
                )
                
                # 记录IP成功注册
                ip_address = get_client_ip(request)
                record_ip_attempt(ip_address, success=True)
                
                messages.success(request, f'用户 "{user.username}" 注册成功！')
                return redirect('users:register')
                
            except Exception as e:
                # 记录失败日志
                log_registration_action(
                    request,
                    'register_failed',
                    target_username=form.cleaned_data.get('username', ''),
                    target_email=form.cleaned_data.get('email', ''),
                    error_message=str(e)
                )
                messages.error(request, f'注册失败：{str(e)}')
        else:
            # 记录表单验证失败
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    field_name = form.fields[field].label if field in form.fields else field
                    error_msg = f"{field_name}: {error}"
                    error_messages.append(error_msg)
                    messages.error(request, error_msg)
            
            log_registration_action(
                request,
                'register_failed',
                target_username=request.POST.get('username', ''),
                target_email=request.POST.get('email', ''),
                error_message='; '.join(error_messages)
            )
            
            # 记录IP失败尝试
            ip_address = get_client_ip(request)
            record_ip_attempt(ip_address, success=False)
    else:
        form = RegisterForm()
    
    # 获取最近的注册日志（仅管理员可见）
    recent_logs = UserRegistrationLog.objects.filter(
        action='register'
    ).select_related('operator', 'target_user').order_by('-created_at')[:10]
    
    return render(request, 'auth/register.html', {
        'form': form,
        'recent_logs': recent_logs,
        'is_admin_register': True  # 标记这是管理员注册页面
    })

@require_http_methods(["GET", "POST"])
def login_view(request):
    """用户登录视图 - 支持登录后跳转"""
    # 获取 next 参数，用于登录后跳转
    next_url = request.GET.get('next') or request.POST.get('next')
    
    print(f"DEBUG: user.is_authenticated = {request.user.is_authenticated}")
    print(f"DEBUG: next_url = {next_url}")

    if request.user.is_authenticated:
        print("DEBUG: 用户已登录，准备跳转")
        if next_url:
            return redirect(next_url)
        return redirect('index')

    if request.method == 'POST':
        print(f"DEBUG: POST 数据 = {request.POST}")
        form = LoginForm(request.POST)

        if form.is_valid():
            print("DEBUG: 表单验证通过")
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            print(f"DEBUG: username={username}, password={'*' * len(password)}")

            user = authenticate(request, username=username, password=password)
            print(f"DEBUG: authenticate 返回 = {user}")

            if user is not None:
                login(request, user)
                print(f"DEBUG: login 成功，准备跳转")
                # 登录成功后跳转到 next 指定的页面
                if next_url:
                    return redirect(next_url)
                return redirect('index')
            else:
                print("DEBUG: 用户名或密码错误")
                messages.error(request, '用户名或密码错误')
        else:
            print(f"DEBUG: 表单验证失败，错误 = {form.errors}")
    else:
        form = LoginForm()

    return render(request, 'auth/login.html', {'form': form, 'next': next_url})

def logout_view(request):
    """用户登出视图"""
    logout(request)
    messages.success(request, '您已成功退出登录')
    return redirect('index')


@login_required
def password_change_view(request):
    """修改密码视图（需旧密码验证）"""
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            # 更新session，避免修改密码后被登出
            update_session_auth_hash(request, request.user)
            messages.success(request, '密码修改成功！')
            return redirect('users:security_settings')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    field_name = form.fields[field].label if field in form.fields else field
                    messages.error(request, f"{field_name}: {error}")
    else:
        form = CustomPasswordChangeForm(user=request.user)

    return render(request, 'auth/password_reset_request.html.html', {'form': form})


# ==================== 忘记密码流程（无邮箱验证版） ====================

def password_reset_request_view(request):
    """忘记密码 - 第一步：输入用户名验证身份"""
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        username = request.POST.get('username')
        try:
            user = CustomUser.objects.get(username=username)
            # 生成重置令牌（使用用户名+时间戳的哈希）
            timestamp = str(int(time.time()))
            token = hashlib.sha256(f"{user.username}{timestamp}{settings.SECRET_KEY}".encode()).hexdigest()[:32]

            # 存储令牌（30分钟有效）
            password_reset_tokens[token] = {
                'user_id': user.id,
                'expires': time.time() + 1800  # 30分钟
            }

            # 直接跳转到重置页面，令牌通过URL传递（简化版，实际应使用更安全的传输方式）
            messages.success(request, '身份验证通过，请设置新密码')
            return redirect('users:password_reset_confirm', token=token)

        except CustomUser.DoesNotExist:
            messages.error(request, '用户名不存在')

    return render(request, 'auth/password_reset_request.html')


def password_reset_confirm_view(request, token):
    """忘记密码 - 第二步：设置新密码"""
    if request.user.is_authenticated:
        return redirect('index')

    # 验证令牌
    token_data = password_reset_tokens.get(token)
    if not token_data:
        messages.error(request, '重置链接无效或已过期')
        return redirect('users:password_reset_request')

    if time.time() > token_data['expires']:
        del password_reset_tokens[token]
        messages.error(request, '重置链接已过期，请重新申请')
        return redirect('users:password_reset_request')

    try:
        user = CustomUser.objects.get(id=token_data['user_id'])
    except CustomUser.DoesNotExist:
        messages.error(request, '用户不存在')
        return redirect('users:password_reset_request')

    if request.method == 'POST':
        form = SetNewPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            user.set_password(new_password)
            user.save()

            # 清除令牌
            del password_reset_tokens[token]

            messages.success(request, '密码重置成功！请使用新密码登录')
            return redirect('users:login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        form = SetNewPasswordForm()

    return render(request, 'auth/password_reset_confirm.html', {
        'form': form,
        'token': token
    })


@login_required
def security_settings_view(request):
    """安全设置页面"""
    return render(request, 'auth/security_settings.html', {
        'user': request.user
    })


# ==================== API接口（供前端AJAX使用） ====================

def check_username_api(request):
    """AJAX检查用户名是否可用"""
    username = request.GET.get('username', '')
    exists = CustomUser.objects.filter(username=username).exists()
    return JsonResponse({
        'available': not exists,
        'message': '用户名已被注册' if exists else '用户名可用'
    })


def check_email_api(request):
    """AJAX检查邮箱是否可用"""
    email = request.GET.get('email', '')
    exists = CustomUser.objects.filter(email=email).exists()
    return JsonResponse({
        'available': not exists,
        'message': '邮箱已被注册' if exists else '邮箱可用'
    })