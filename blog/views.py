from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Comment
from .models import Course, Chapter, Question, PracticeRecord, ErrorNotebook, CourseMaterial, DownloadRecord, CalendarEvent
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect, Http404
from django.http import JsonResponse, FileResponse, HttpResponse, StreamingHttpResponse
from django.utils.encoding import escape_uri_path
from django.db import IntegrityError, transaction
import os
import re
import logging

logger = logging.getLogger('django')

def index(request):
    """首页视图"""
    return render(request, 'index.html')

def get_user_learning_stats(user):
    """获取用户学习统计"""
    if not user.is_authenticated:
        return {
            'completed_courses': 0,
            'completed_exercises': 0,
            'study_hours': 0,
            'average_accuracy': 0,
        }
    
    # 获取用户的练习记录
    practice_records = PracticeRecord.objects.filter(user=user)
    completed_exercises = practice_records.count()
    
    # 计算完成的课程数（至少完成一道题的课程）
    completed_courses = PracticeRecord.objects.filter(user=user).values('course').distinct().count()
    
    # 估算练习题学习时长（每道题平均3分钟）
    exercise_study_minutes = completed_exercises * 3
    
    # 获取知识学习页面已完成的小章节数量
    try:
        from .models import ChapterProgress
        completed_chapters_count = ChapterProgress.objects.filter(
            user=user, 
            is_completed=True
        ).count()
    except Exception:
        completed_chapters_count = 0
    
    # 估算知识学习时长（每完成一个小章节按5分钟计算）
    knowledge_study_minutes = completed_chapters_count * 5
    
    # 总学习时长（练习题 + 知识学习）
    total_study_minutes = exercise_study_minutes + knowledge_study_minutes
    study_hours = round(total_study_minutes / 60, 1)
    
    # 计算平均正确率
    if completed_exercises > 0:
        correct_count = practice_records.filter(is_correct=True).count()
        average_accuracy = round(correct_count / completed_exercises * 100, 1)
    else:
        average_accuracy = 0
    
    return {
        'completed_courses': completed_courses,
        'completed_exercises': completed_exercises,
        'completed_chapters': completed_chapters_count,
        'study_hours': study_hours,
        'average_accuracy': average_accuracy,
    }

def community(request):
    """学习社区"""
    chapter = request.GET.get('chapter', '')
    if chapter:
        posts = Post.objects.filter(chapter=chapter)
    else:
        posts = Post.objects.all()
    
    return render(request, 'community.html', {
        'posts': posts,
        'current_chapter': chapter,
        'chapter_choices': Post.CHAPTER_CHOICES,
    })

def post_detail(request, post_id):
    """帖子详情"""
    post = get_object_or_404(Post, id=post_id)
    # 增加浏览量
    post.views += 1
    post.save()
    
    return render(request, 'post_detail.html', {
        'post': post,
        'comments': post.comments.all(),
        'chapter_choices': Post.CHAPTER_CHOICES,
    })

@login_required
def create_post(request):
    """创建帖子"""
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        chapter = request.POST.get('chapter', 'general')
        
        if title and content:
            post = Post.objects.create(
                title=title,
                content=content,
                chapter=chapter,
                author=request.user.username
            )
            return redirect('post_detail', post_id=post.id)
    
    return render(request, 'create_post.html', {
        'chapter_choices': Post.CHAPTER_CHOICES
    })

@login_required
def add_comment(request, post_id):
    """添加评论"""
    post = get_object_or_404(Post, id=post_id)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Comment.objects.create(
                post=post,
                content=content,
                author=request.user.username
            )
    
    return redirect('post_detail', post_id=post.id)


def course_intro(request):
    """课程介绍页面"""
    return render(request, 'course_intro.html')

def teaching_resources(request):
    """教学资源页面"""
    return render(request, 'teaching_resources.html')

def teaching_materials(request):
    """教学资料页面"""
    return render(request, 'teaching_resources.html')

def simulation_platform(request):
    """仿真平台页面"""
    return render(request, 'simulation_platform.html')

def exercises_cases(request):
    """习题案例页面"""
    return render(request, 'blog/exercises_cases.html')

def error_notebook(request):
    """错题本页面"""
    return render(request, 'blog/error_notebook.html')

def calendar(request):
    """日历页面"""
    return render(request, 'calendar.html')


@require_http_methods(["GET"])
def get_courses(request):
    """获取所有课程"""
    courses = Course.objects.filter(is_active=True) if hasattr(Course, 'is_active') else Course.objects.all()
    return JsonResponse({
        'courses': [{'code': c.code, 'name': c.name} for c in courses]
    })


@require_http_methods(["GET"])
def get_chapters(request):
    """获取指定课程的所有章节"""
    course_code = request.GET.get('course')
    if not course_code:
        return JsonResponse({'error': '缺少课程代码'}, status=400)
    
    try:
        course = Course.objects.get(code=course_code)
        chapters = Chapter.objects.filter(course=course).order_by('order')
        return JsonResponse({
            'chapters': [{'code': c.code, 'name': c.name} for c in chapters]
        })
    except Course.DoesNotExist:
        return JsonResponse({'error': '课程不存在'}, status=404)


@require_http_methods(["GET"])
def get_questions(request):
    """获取题目列表"""
    course_code = request.GET.get('course')
    chapter_code = request.GET.get('chapter')
    question_type = request.GET.get('type')  # 题型筛选参数
    difficulty = request.GET.get('difficulty')  # 难度筛选参数
    count = request.GET.get('count')  # 题目数量限制
    
    if not course_code:
        return JsonResponse({'error': '缺少课程代码'}, status=400)
    
    try:
        course = Course.objects.get(code=course_code)
    except Course.DoesNotExist:
        return JsonResponse({'error': '课程不存在'}, status=404)
    
    # 基础查询集
    queryset = Question.objects.filter(course=course, is_active=True)
    
    # 章节筛选
    if chapter_code:
        try:
            chapter = Chapter.objects.get(course=course, code=chapter_code)
            queryset = queryset.filter(chapter=chapter)
        except Chapter.DoesNotExist:
            return JsonResponse({'error': '章节不存在'}, status=404)
    
    # 题型筛选
    if question_type:
        valid_types = ['single', 'multiple', 'judge']
        if question_type in valid_types:
            queryset = queryset.filter(question_type=question_type)
    
    # 难度筛选
    if difficulty:
        try:
            difficulty_int = int(difficulty)
            queryset = queryset.filter(difficulty=difficulty_int)
        except (ValueError, TypeError):
            pass  # 忽略无效的难度参数
    
    # 随机排序
    queryset = queryset.order_by('?')
    
    # 限制题目数量
    if count:
        try:
            count_int = int(count)
            if count_int > 0:
                queryset = queryset[:count_int]
        except (ValueError, TypeError):
            pass  # 忽略无效的数量参数
    
    # 构建返回数据
    questions = []
    for q in queryset:
        questions.append({
            'id': q.id,
            'question_type': q.question_type,
            'difficulty': q.difficulty,
            'content': q.content,
            'options': q.options,
            'correct_answer': q.correct_answer,
            'explanation': q.explanation,
            'chapter': q.chapter.name if q.chapter else '综合',
        })
    
    return JsonResponse({
        'questions': questions,
        'total': len(questions)
    })


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def submit_answer(request):
    """提交答案"""
    import json
    
    try:
        data = json.loads(request.body)
        question_id = data.get('question_id')
        user_answer = data.get('answer', '').strip().upper()
        
        if not question_id:
            return JsonResponse({'error': '缺少题目ID'}, status=400)
        
        try:
            question = Question.objects.select_related('course', 'chapter').get(id=question_id)
        except Question.DoesNotExist:
            logger.warning(f"[SUBMIT] 题目不存在 id={question_id}, user={request.user.username}")
            return JsonResponse({'error': '题目不存在'}, status=404)
        
        is_correct = user_answer == question.correct_answer.upper()
        course_code = question.course.code if question.course else 'unknown'
        logger.info(f"[SUBMIT] user={request.user.username}, qid={question_id}, course={course_code}, answer={user_answer}, correct={is_correct}")
        
        PracticeRecord.objects.create(
            user=request.user,
            question=question,
            course=question.course,
            user_answer=user_answer,
            is_correct=is_correct
        )
        
        if not is_correct:
            try:
                with transaction.atomic():
                    error_note, created = ErrorNotebook.objects.get_or_create(
                        user=request.user,
                        question=question,
                        defaults={
                            'course': question.course,
                            'error_count': 1
                        }
                    )
                    if not created:
                        error_note.error_count += 1
                        error_note.save()
                logger.info(f"[SUBMIT] 错题{'已创建' if created else '已更新'} id={error_note.id}, count={error_note.error_count}, course={course_code}")
            except IntegrityError as ie:
                logger.error(f"[SUBMIT] 错题写入IntegrityError: {ie}, user={request.user.username}, qid={question_id}")
                return JsonResponse({'correct': is_correct, 'correct_answer': question.correct_answer, 'explanation': question.explanation, 'note': '错题已存在'})
        
        return JsonResponse({
            'correct': is_correct,
            'correct_answer': question.correct_answer,
            'explanation': question.explanation,
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': '无效的JSON数据'}, status=400)
    except Exception as e:
        logger.exception(f"[SUBMIT] 未预期异常: {e}, user={request.user.username if request.user.is_authenticated else 'anonymous'}")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def get_error_notebook(request):
    """获取用户的错题本"""
    user = request.user
    course_code = request.GET.get('course', '')
    
    base_queryset = ErrorNotebook.objects.filter(user=request.user)
    
    # 课程筛选
    if course_code:
        try:
            course = Course.objects.get(code=course_code)
            base_queryset = base_queryset.filter(course=course)
        except Course.DoesNotExist:
            pass
    
    # 获取统计数据
    total = base_queryset.count()
    mastered = base_queryset.filter(is_mastered=True).count()
    unmastered = base_queryset.filter(is_mastered=False).count()
    
    # 只显示未掌握的错题
    errors = base_queryset.filter(is_mastered=False).select_related('question', 'course')
    
    error_list = []
    for error in errors:
        error_list.append({
            'id': error.id,
            'course': error.course.name,
            'course_code': error.course.code,
            'chapter': error.question.chapter.name if error.question.chapter else '综合',
            'content': error.question.content,
            'type': error.question.question_type,
            'difficulty': error.question.difficulty,
            'error_count': error.error_count,
            'last_error_time': error.last_error_time.strftime('%Y-%m-%d %H:%M'),
            'options': error.question.options or [],
            'correct_answer': error.question.correct_answer,
            'explanation': error.question.explanation or '暂无解析',
        })
    
    return JsonResponse({
        'errors': error_list,
        'total': total,
        'unmastered': unmastered,
        'mastered': mastered
    })


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def mark_as_mastered(request):
    """标记错题为已掌握"""
    import json
    
    try:
        data = json.loads(request.body)
        error_id = data.get('error_id')
        
        try:
            error_note = ErrorNotebook.objects.get(id=error_id, user=request.user)
            error_note.is_mastered = True
            error_note.save()
            return JsonResponse({'success': True})
        except ErrorNotebook.DoesNotExist:
            return JsonResponse({'error': '错题记录不存在'}, status=404)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': '无效的JSON数据'}, status=400)


def learning_resources(request):
    """学习资源页面 - 资料下载中心"""
    # 获取所有课程
    courses = Course.objects.all()

    # 获取当前选中的课程和章节
    course_code = request.GET.get('course', '')
    chapter_code = request.GET.get('chapter', '')

    # 构建查询
    materials = CourseMaterial.objects.filter(is_public=True)

    if course_code:
        materials = materials.filter(course__code=course_code)
    if chapter_code:
        materials = materials.filter(chapter__code=chapter_code)

    # 搜索功能
    search_query = request.GET.get('search', '')
    if search_query:
        materials = materials.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # 文件类型筛选
    file_type = request.GET.get('type', '')
    if file_type:
        materials = materials.filter(file_type=file_type)

    context = {
        'courses': courses,
        'materials': materials,
        'current_course': course_code,
        'current_chapter': chapter_code,
        'search_query': search_query,
        'file_types': CourseMaterial.FILE_TYPES,
    }
    return render(request, 'blog/learning_resources.html', context)


@login_required
@require_http_methods(["POST"])
def upload_material(request):
    """上传资料（仅管理员）"""
    if not request.user.is_staff:
        return JsonResponse({'error': '权限不足'}, status=403)
    
    try:
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        course_id = request.POST.get('course')
        chapter_id = request.POST.get('chapter')
        file = request.FILES.get('file')
        
        if not all([title, course_id, file]):
            return JsonResponse({'error': '缺少必要字段'}, status=400)
        
        course = Course.objects.get(id=course_id)
        chapter = Chapter.objects.get(id=chapter_id) if chapter_id else None
        
        material = CourseMaterial.objects.create(
            title=title,
            description=description,
            course=course,
            chapter=chapter,
            file=file,
            uploader=request.user
        )
        
        return JsonResponse({
            'success': True,
            'material_id': material.id,
            'message': '上传成功'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def serve_video(request, filename):
    """视频流服务——流式传输避免内存溢出，支持Range请求和跨域"""
    from django.conf import settings

    video_path = os.path.join(settings.BASE_DIR, 'static', 'video', filename)
    if not os.path.exists(video_path):
        video_path = os.path.join(settings.STATIC_ROOT, 'video', filename)
    if not os.path.exists(video_path):
        raise Http404('视频文件不存在')

    ext = os.path.splitext(filename)[1].lower()
    content_type_map = {
        '.mp4': 'video/mp4',
        '.webm': 'video/webm',
        '.ogv': 'video/ogg',
        '.mov': 'video/quicktime',
    }
    content_type = content_type_map.get(ext, 'video/mp4')

    file_size = os.path.getsize(video_path)
    range_header = request.META.get('HTTP_RANGE', '').strip()
    response = None

    if range_header:
        range_match = re.match(r'bytes=(\d*)-(\d*)', range_header)

        if range_match:
            first_byte_str = range_match.group(1)
            last_byte_str = range_match.group(2)

            if first_byte_str == '' and last_byte_str == '':
                start = 0
                end = file_size - 1
            else:
                start = int(first_byte_str) if first_byte_str else 0
                if last_byte_str:
                    end = int(last_byte_str)
                    end = min(end, file_size - 1)
                else:
                    end = file_size - 1

            if start > end or start >= file_size:
                response = HttpResponse(status=416)
                response['Content-Range'] = 'bytes */{0}'.format(file_size)
                return response

            content_length = end - start + 1

            with open(video_path, 'rb') as f:
                f.seek(start)
                file_data = f.read(content_length)

            response = HttpResponse(file_data, content_type=content_type, status=206)
            response['Content-Range'] = 'bytes {0}-{1}/{2}'.format(start, end, file_size)
            response['Content-Length'] = str(content_length)

    if response is None:
        def file_iterator(path, chunk_size=128 * 1024):
            with open(path, 'rb') as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk

        response = StreamingHttpResponse(file_iterator(video_path), content_type=content_type)
        response['Content-Length'] = str(file_size)

    response['Accept-Ranges'] = 'bytes'
    response['Cache-Control'] = 'public, max-age=86400'
    response['Content-Disposition'] = 'inline; filename="' + filename + '"'
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    response['Access-Control-Allow-Headers'] = 'Range, Content-Type'
    return response


@login_required
def download_material(request, material_id):
    """下载资料"""
    material = get_object_or_404(CourseMaterial, id=material_id)
    
    # 增加下载计数
    material.download_count += 1
    material.save()
    
    # 记录下载
    DownloadRecord.objects.create(
        user=request.user,
        material=material,
        ip_address=get_client_ip(request)
    )
    
    # 返回文件
    response = FileResponse(material.file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = f'attachment; filename="{escape_uri_path(material.file.name.split("/")[-1])}"'
    return response


def get_client_ip(request):
    """获取客户端IP"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def learning_progress(request):
    """学习进度可视化页面 - 显示用户真实学习数据"""
    context = {
        'user_stats': {
            'study_hours': 0,
            'completed_exercises': 0,
            'average_accuracy': 0,
            'completed_chapters': 0,
            'total_chapters': 0,
        },
        'chapter_progress': [],
        'accuracy_trend': [],
        'study_time_distribution': [],
        'is_authenticated': request.user.is_authenticated,
    }
    
    if request.user.is_authenticated:
        user = request.user
        
        try:
            # 获取用户基础统计数据
            base_stats = get_user_learning_stats(user)
            context['user_stats']['study_hours'] = base_stats['study_hours']
            context['user_stats']['completed_exercises'] = base_stats['completed_exercises']
            
            # 获取用户的练习记录
            practice_records = PracticeRecord.objects.filter(user=user).select_related('question', 'course')
            
            # 计算平均正确率
            if practice_records.exists():
                total_records = practice_records.count()
                correct_records = practice_records.filter(is_correct=True).count()
                context['user_stats']['average_accuracy'] = round((correct_records / total_records) * 100, 1)
            
            # 从ChapterProgress模型获取知识学习页面的章节完成度
            try:
                from .models import ChapterProgress
                chapter_progress_records = ChapterProgress.objects.filter(user=user)
                
                # 定义课程章节结构（主章节 -> 小章节列表）
                COURSE_STRUCTURE = {
                    'ee': {
                        '第0章': ['ee/ch0-1'],
                        '第1章': ['ee/ch1-1', 'ee/ch1-2', 'ee/ch1-3', 'ee/ch1-4', 'ee/ch1-5', 'ee/ch1-6', 'ee/ch1-7'],
                        '第2章': ['ee/ch2-1', 'ee/ch2-2', 'ee/ch2-3', 'ee/ch2-4', 'ee/ch2-5', 'ee/ch2-6', 'ee/ch2-7'],
                        '第3章': ['ee/ch3-1', 'ee/ch3-2', 'ee/ch3-3', 'ee/ch3-4', 'ee/ch3-5', 'ee/ch3-6', 'ee/ch3-7'],
                        '第4章': ['ee/ch4-1', 'ee/ch4-2', 'ee/ch4-3', 'ee/ch4-4', 'ee/ch4-5'],
                        '第5章': ['ee/ch5-1', 'ee/ch5-2', 'ee/ch5-3', 'ee/ch5-4'],
                        '第6章': ['ee/ch6-1', 'ee/ch6-2', 'ee/ch6-3', 'ee/ch6-4', 'ee/ch6-5'],
                        '第7章': ['ee/ch7-1', 'ee/ch7-2', 'ee/ch7-3', 'ee/ch7-4', 'ee/ch7-5', 'ee/ch7-6'],
                        '第8章': ['ee/ch8-1', 'ee/ch8-2', 'ee/ch8-3', 'ee/ch8-4', 'ee/ch8-5', 'ee/ch8-6', 'ee/ch8-7']
                    },
                    'mw': {
                        '第0章': ['mw/ch0-1'],
                        '第1章': ['mw/ch1-1', 'mw/ch1-2', 'mw/ch1-3', 'mw/ch1-4'],
                        '第2章': ['mw/ch2-1', 'mw/ch2-2', 'mw/ch2-3', 'mw/ch2-4', 'mw/ch2-5', 'mw/ch2-6', 'mw/ch2-7'],
                        '第3章': ['mw/ch3-1', 'mw/ch3-2', 'mw/ch3-3', 'mw/ch3-4', 'mw/ch3-5'],
                        '第4章': ['mw/ch4-1', 'mw/ch4-2', 'mw/ch4-3', 'mw/ch4-4', 'mw/ch4-5', 'mw/ch4-6', 'mw/ch4-7'],
                        '第5章': ['mw/ch5-1', 'mw/ch5-2', 'mw/ch5-3', 'mw/ch5-4', 'mw/ch5-5', 'mw/ch5-6', 'mw/ch5-7'],
                        '第6章': ['mw/ch6-1', 'mw/ch6-2', 'mw/ch6-3', 'mw/ch6-4', 'mw/ch6-5', 'mw/ch6-6', 'mw/ch6-7'],
                        '第7章': ['mw/ch7-1', 'mw/ch7-2', 'mw/ch7-3', 'mw/ch7-4', 'mw/ch7-5'],
                        '第8章': ['mw/ch8-1', 'mw/ch8-2', 'mw/ch8-3', 'mw/ch8-4', 'mw/ch8-5', 'mw/ch8-6']
                    }
                }
                
                # 获取用户已完成的小章节ID列表
                completed_subchapters = set(
                    chapter_progress_records.filter(is_completed=True)
                    .values_list('chapter_id', flat=True)
                )
                
                # 调试：输出所有存储的章节ID
                all_stored_records = list(chapter_progress_records.filter(is_completed=True).values('chapter_id', 'chapter_name', 'course_code'))
                print(f"DEBUG - 用户已完成的小章节记录: {all_stored_records}")
                print(f"DEBUG - 已完成小章节ID集合: {completed_subchapters}")
                
                # 计算各课程的主章节完成数量
                def calculate_main_chapter_progress(course_code):
                    structure = COURSE_STRUCTURE.get(course_code, {})
                    total_main = len(structure)
                    completed_main = 0
                    
                    for main_chapter, subchapters in structure.items():
                        # 检查该主章节下的所有小章节是否都已完成
                        completed_count = sum(1 for sub_id in subchapters if sub_id in completed_subchapters)
                        is_complete = all(sub_id in completed_subchapters for sub_id in subchapters)
                        
                        print(f"DEBUG - {course_code} {main_chapter}: 已完成{completed_count}/{len(subchapters)}, 是否全部完成: {is_complete}")
                        
                        if is_complete:
                            completed_main += 1
                    
                    result = {
                        'completed': completed_main,
                        'total': total_main,
                        'rate': round(completed_main / total_main * 100, 1) if total_main > 0 else 0
                    }
                    print(f"DEBUG - {course_code} 最终结果: {result}")
                    return result
                
                ee_progress = calculate_main_chapter_progress('ee')
                mw_progress = calculate_main_chapter_progress('mw')
                
                context['chapter_progress_knowledge'] = {
                    'ee': ee_progress,
                    'mw': mw_progress
                }
                
                # 计算章节完成度（用于环形图）- 基于知识学习页面的主章节完成情况
                # 合并两个课程的章节，总共18章（ee 9章 + mw 9章）
                chapter_progress = []
                completed_chapters = 0
                in_progress_chapters = 0
                not_started_chapters = 0
                
                for course_code, structure in COURSE_STRUCTURE.items():
                    for main_chapter, subchapters in structure.items():
                        completed_count = sum(1 for sub_id in subchapters if sub_id in completed_subchapters)
                        total_count = len(subchapters)
                        
                        if completed_count == total_count:
                            status = 'completed'
                            completed_chapters += 1
                        elif completed_count > 0:
                            status = 'in_progress'
                            in_progress_chapters += 1
                        else:
                            status = 'not_started'
                            not_started_chapters += 1
                        
                        chapter_name = f"{'电磁场' if course_code == 'ee' else '微波'}{main_chapter}"
                        progress_value = round((completed_count / total_count) * 100, 1) if total_count > 0 else 0
                        
                        chapter_progress.append({
                            'name': chapter_name,
                            'value': progress_value,
                            'status': status,
                            'answered': completed_count,
                            'total': total_count,
                        })
                
                context['user_stats']['total_chapters'] = len(chapter_progress)
                context['user_stats']['completed_chapters'] = completed_chapters
                context['chapter_progress'] = chapter_progress
                
                print(f"DEBUG - 章节完成度统计: 已完成{completed_chapters}, 进行中{in_progress_chapters}, 未开始{not_started_chapters}")
                print(f"DEBUG - 主章节完成进度 - EE: {ee_progress}, MW: {mw_progress}")
            except Exception as e:
                print(f"获取章节进度记录出错: {e}")
                import traceback
                traceback.print_exc()
                context['chapter_progress_knowledge'] = {
                    'ee': {'completed': 0, 'total': 9, 'rate': 0},
                    'mw': {'completed': 0, 'total': 9, 'rate': 0}
                }
                # 出错时使用原来的练习记录数据
                all_chapters = Chapter.objects.all()
                total_chapters = all_chapters.count()
                context['user_stats']['total_chapters'] = total_chapters
                
                chapter_progress = []
                completed_chapters = 0
                
                for chapter in all_chapters:
                    chapter_questions = Question.objects.filter(chapter=chapter)
                    total_questions = chapter_questions.count()
                    chapter_records = practice_records.filter(question__chapter=chapter)
                    answered_questions = chapter_records.values('question').distinct().count()
                    
                    if total_questions > 0:
                        progress_value = round((answered_questions / total_questions) * 100, 1)
                    else:
                        progress_value = 0
                    
                    if progress_value >= 100:
                        status = 'completed'
                        completed_chapters += 1
                    elif progress_value > 0:
                        status = 'in_progress'
                    else:
                        status = 'not_started'
                    
                    chapter_progress.append({
                        'name': chapter.name,
                        'value': progress_value,
                        'status': status,
                        'answered': answered_questions,
                        'total': total_questions,
                    })
                
                context['user_stats']['completed_chapters'] = completed_chapters
                context['chapter_progress'] = chapter_progress
            
            # 计算正确率趋势（按日期分组）
            from django.db.models import Count, Avg
            from django.db.models.functions import TruncDate
            
            daily_stats = practice_records.annotate(
                date=TruncDate('practice_time')
            ).values('date').annotate(
                total=Count('id'),
                correct=Count('id', filter=Q(is_correct=True))
            ).order_by('date')[:7]
            
            accuracy_trend = []
            for stat in daily_stats:
                if stat['date']:
                    date_str = stat['date'].strftime('%m-%d')
                    accuracy = round((stat['correct'] / stat['total']) * 100, 1) if stat['total'] > 0 else 0
                    accuracy_trend.append({
                        'date': date_str,
                        'accuracy': accuracy,
                    })
            
            context['accuracy_trend'] = accuracy_trend
            
            # 学习时间分布（按小时段统计）- 包含练习题和知识学习
            # 使用 Python 处理时间分布（SQLite 对 ExtractHour 支持不完善）
            
            # 调试：检查当前用户和practice_records
            print(f"DEBUG - 当前用户ID: {user.id}, 用户名: {user.username}")
            print(f"DEBUG - practice_records 过滤条件: user={user.id}")
            print(f"DEBUG - practice_records 数量: {practice_records.count()}")
            
            # 检查数据库中所有记录的数量
            total_records_all = PracticeRecord.objects.count()
            total_records_user = PracticeRecord.objects.filter(user=user).count()
            print(f"DEBUG - 数据库中所有练习记录数: {total_records_all}")
            print(f"DEBUG - 当前用户的练习记录数: {total_records_user}")
            
            if practice_records.count() > 0:
                first_record = practice_records.first()
                print(f"DEBUG - 第一条记录时间: {first_record.practice_time}, 用户ID: {first_record.user_id}")
            
            # 初始化24小时时间分布
            time_distribution = [0] * 24
            
            # 时区偏移：UTC+8（东八区）
            TIMEZONE_OFFSET = 8
            
            # 练习题时间分布（每题计1单位，约3分钟）
            for record in practice_records:
                if record.practice_time:
                    # UTC时间转换为东八区时间
                    local_hour = (record.practice_time.hour + TIMEZONE_OFFSET) % 24
                    time_distribution[local_hour] += 1
            
            print(f"DEBUG - 练习题时间分布: {time_distribution}")
            print(f"DEBUG - 练习题活动总数: {sum(time_distribution)}")
            
            # 知识学习时间分布（每个完成的小章节计1单位，约5分钟）
            try:
                from .models import ChapterProgress
                knowledge_records = ChapterProgress.objects.filter(
                    user=user,
                    is_completed=True,
                    completed_at__isnull=False
                )
                
                # 检查数据库中所有知识学习记录
                total_knowledge_all = ChapterProgress.objects.filter(is_completed=True).count()
                total_knowledge_user = knowledge_records.count()
                print(f"DEBUG - 数据库中所有知识学习完成记录数: {total_knowledge_all}")
                print(f"DEBUG - 当前用户的知识学习完成记录数: {total_knowledge_user}")
                
                if knowledge_records.count() > 0:
                    first_knowledge = knowledge_records.first()
                    print(f"DEBUG - 第一条知识记录完成时间: {first_knowledge.completed_at}, 用户ID: {first_knowledge.user_id}")
                
                for record in knowledge_records:
                    if record.completed_at:
                        # UTC时间转换为东八区时间
                        local_hour = (record.completed_at.hour + TIMEZONE_OFFSET) % 24
                        time_distribution[local_hour] += 1
                        
                print(f"DEBUG - 加入知识学习后时间分布: {time_distribution}")
            except Exception as e:
                print(f"DEBUG - 知识学习时间分布查询出错: {e}")
            
            context['study_time_distribution'] = time_distribution
            
            # 调试输出
            print(f"DEBUG - 最终学习时间分布数据: {time_distribution}")
            print(f"DEBUG - 总学习活动数: {sum(time_distribution)}")
            
        except Exception as e:
            print(f"获取学习进度数据出错: {e}")
            import traceback
            traceback.print_exc()
    
    return render(request, 'learning_progress.html', context)


@require_http_methods(["GET"])
def get_user_stats(request):
    """获取当前用户的学习统计数据（API接口）"""
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': '用户未登录',
            'data': {
                'completed_courses': 0,
                'completed_exercises': 0,
                'study_hours': 0,
            }
        })
    
    try:
        stats = get_user_learning_stats(request.user)
        return JsonResponse({
            'success': True,
            'data': stats
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })


def knowledge(request):
    """课程知识总览页面"""
    return render(request, 'knowledge.html')


def knowledge_ee(request):
    """电磁场与电磁波课程学习页面"""
    return render(request, 'knowledge_ee.html')


def knowledge_mw(request):
    """微波工程课程学习页面"""
    return render(request, 'knowledge_mw.html')


@login_required
@require_http_methods(["GET"])
def get_calendar_events(request):
    """获取用户的日历事件"""
    user = request.user
    events = CalendarEvent.objects.filter(user=user)
    
    # 支持两种参数格式：
    # 1. year=2024&month=12（前端当前使用的格式）
    # 2. month=2024-12（旧格式，向后兼容）
    
    year = request.GET.get('year')
    month = request.GET.get('month')
    
    if year and month:
        # 新格式：year=2024&month=12
        try:
            year = int(year)
            month = int(month)
            if 1 <= month <= 12:
                month_str = f"{year}-{month:02d}"
                events = events.filter(date__startswith=month_str)
        except (ValueError, TypeError):
            pass
    elif month and '-' in str(month):
        # 旧格式：month=2024-12（向后兼容）
        events = events.filter(date__startswith=month)
    
    event_list = []
    for event in events:
        event_list.append({
            'id': event.id,
            'title': event.title,
            'date': event.date.strftime('%Y-%m-%d'),
            'time': event.time.strftime('%H:%M') if event.time else None,
            'location': event.location,
            'type': event.event_type,
            'description': event.description,
        })
    
    return JsonResponse({
        'success': True,
        'events': event_list
    })


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def create_calendar_event(request):
    """创建日历事件"""
    import json
    
    try:
        data = json.loads(request.body)
        
        # 表单验证
        title = data.get('title', '').strip()
        date = data.get('date', '').strip()
        
        if not title:
            return JsonResponse({
                'success': False, 
                'error': '请输入课程名称',
                'field': 'title',
                'message': '课程名称不能为空'
            })
        
        if not date:
            return JsonResponse({
                'success': False, 
                'error': '请选择日期',
                'field': 'date',
                'message': '日期不能为空'
            })
        
        # 验证日期格式
        try:
            from datetime import datetime
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            return JsonResponse({
                'success': False, 
                'error': '日期格式不正确，请使用YYYY-MM-DD格式',
                'field': 'date'
            })
        
        # 验证事件类型
        valid_types = ['theory', 'lab', 'exam', 'assignment', 'review', 'other']
        event_type = data.get('type', 'other')
        if event_type not in valid_types:
            event_type = 'other'
        
        event = CalendarEvent.objects.create(
            user=request.user,
            title=title,
            date=date,
            time=data.get('time') or None,
            location=data.get('location', ''),
            event_type=event_type,
            description=data.get('description', '')
        )
        
        return JsonResponse({
            'success': True,
            'event_id': event.id,
            'message': '课程添加成功',
            'event': {
                'id': event.id,
                'title': event.title,
                'date': event.date,
                'time': event.time,
                'location': event.location,
                'type': event.event_type,
                'description': event.description
            }
        })
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False, 
            'error': '请求数据格式错误，请检查输入内容',
            'message': '数据格式错误'
        })
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'error': f'添加失败：{str(e)}',
            'message': '操作失败，请稍后重试'
        })


@login_required
@require_http_methods(["POST", "PUT"])
@csrf_exempt
def update_calendar_event(request, event_id):
    """更新日历事件"""
    import json
    
    try:
        event = CalendarEvent.objects.get(id=event_id, user=request.user)
        data = json.loads(request.body)
        
        # 表单验证
        title = data.get('title', '').strip()
        date = data.get('date', '').strip()
        
        if not title:
            return JsonResponse({'success': False, 'error': '课程名称不能为空', 'field': 'title'})
        
        if not date:
            return JsonResponse({'success': False, 'error': '日期不能为空', 'field': 'date'})
        
        event.title = title
        event.date = date
        event.time = data.get('time') or None
        event.location = data.get('location', '')
        event.event_type = data.get('type', 'other')
        event.description = data.get('description', '')
        event.save()
        
        return JsonResponse({
            'success': True, 
            'event_id': event.id,
            'message': '更新成功',
            'event': {
                'id': event.id,
                'title': event.title,
                'date': event.date,
                'time': event.time,
                'location': event.location,
                'type': event.event_type,
                'description': event.description
            }
        })
    except CalendarEvent.DoesNotExist:
        return JsonResponse({'success': False, 'error': '课程不存在或您没有权限修改'})
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': '请求数据格式错误'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'更新失败：{str(e)}'})


@login_required
@require_http_methods(["POST", "DELETE"])
@csrf_exempt
def delete_calendar_event(request, event_id):
    """删除日历事件"""
    try:
        event = CalendarEvent.objects.get(id=event_id, user=request.user)
        event.delete()
        return JsonResponse({
            'success': True, 
            'message': '删除成功',
            'deleted_id': event_id
        })
    except CalendarEvent.DoesNotExist:
        return JsonResponse({'success': False, 'error': '课程不存在或您没有权限删除'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'删除失败：{str(e)}'})


@login_required
@require_http_methods(["GET"])
def check_calendar_auth(request):
    """检查用户认证状态"""
    return JsonResponse({
        'is_authenticated': True,
        'username': request.user.username,
        'user_id': request.user.id,
    })


# ==================== 章节学习进度 API ====================

@login_required
@require_http_methods(["GET"])
def get_chapter_progress(request):
    """获取用户的章节学习进度"""
    user = request.user
    course_code = request.GET.get('course', '')
    
    from .models import ChapterProgress
    
    query = ChapterProgress.objects.filter(user=user)
    if course_code:
        query = query.filter(course_code=course_code)
    
    progress_list = list(query.values('chapter_id', 'chapter_name', 'course_code', 
                                       'is_completed', 'completed_at'))
    
    total = query.count()
    completed = query.filter(is_completed=True).count()
    
    return JsonResponse({
        'success': True,
        'data': {
            'progress_list': progress_list,
            'stats': {
                'total': total,
                'completed': completed,
                'progress_rate': round(completed / total * 100, 1) if total > 0 else 0
            }
        }
    })


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def update_chapter_progress(request):
    """更新章节学习进度（标记完成/取消完成）"""
    import json
    from datetime import datetime
    from .models import ChapterProgress
    
    try:
        data = json.loads(request.body)
        chapter_id = data.get('chapter_id')
        chapter_name = data.get('chapter_name', '')
        course_code = data.get('course_code', '')
        is_completed = data.get('is_completed', False)
        
        if not chapter_id:
            return JsonResponse({'success': False, 'message': '缺少章节ID'})
        
        progress, created = ChapterProgress.objects.get_or_create(
            user=request.user,
            chapter_id=chapter_id,
            defaults={
                'chapter_name': chapter_name,
                'course_code': course_code,
                'is_completed': is_completed,
                'completed_at': datetime.now() if is_completed else None,
                'completed_subtasks_count': 1 if is_completed else 0,
                'total_subtasks_count': 1,
                'subtasks': {}
            }
        )
        
        if not created:
            progress.is_completed = is_completed
            progress.completed_at = datetime.now() if is_completed else None
            progress.completed_subtasks_count = 1 if is_completed else 0
            progress.save()
        
        return JsonResponse({
            'success': True,
            'message': '已标记为完成' if is_completed else '已取消完成标记',
            'data': {
                'chapter_id': progress.chapter_id,
                'is_completed': progress.is_completed,
                'completed_at': progress.completed_at.isoformat() if progress.completed_at else None
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': '无效的JSON数据'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def sync_chapter_progress(request):
    """批量同步章节学习进度（用于本地存储数据上传到服务器）"""
    import json
    from datetime import datetime
    from .models import ChapterProgress
    
    try:
        data = json.loads(request.body)
        progress_data = data.get('progress_data', [])
        
        if not isinstance(progress_data, list):
            return JsonResponse({'success': False, 'message': '数据格式错误'})
        
        updated_count = 0
        for item in progress_data:
            chapter_id = item.get('chapter_id')
            if not chapter_id:
                continue
                
            is_completed = item.get('is_completed', False)
            progress, created = ChapterProgress.objects.update_or_create(
                user=request.user,
                chapter_id=chapter_id,
                defaults={
                    'chapter_name': item.get('chapter_name', ''),
                    'course_code': item.get('course_code', ''),
                    'is_completed': is_completed,
                    'completed_at': datetime.fromisoformat(item['completed_at']) if item.get('completed_at') else None,
                    'completed_subtasks_count': 1 if is_completed else 0,
                    'total_subtasks_count': 1,
                    'subtasks': {}
                }
            )
            updated_count += 1
        
        return JsonResponse({
            'success': True,
            'message': f'成功同步 {updated_count} 条记录',
            'updated_count': updated_count
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': '无效的JSON数据'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@login_required
@require_http_methods(["GET"])
def get_learning_progress_knowledge(request):
    """获取用户知识学习页面的章节完成进度（用于学习进度页面实时刷新）"""
    from .models import ChapterProgress
    from datetime import datetime
    
    try:
        user = request.user
        chapter_progress_records = ChapterProgress.objects.filter(user=user)
        
        # 定义课程章节结构（主章节 -> 小章节列表）
        COURSE_STRUCTURE = {
            'ee': {
                '第0章': ['ee/ch0-1'],
                '第1章': ['ee/ch1-1', 'ee/ch1-2', 'ee/ch1-3', 'ee/ch1-4', 'ee/ch1-5', 'ee/ch1-6', 'ee/ch1-7'],
                '第2章': ['ee/ch2-1', 'ee/ch2-2', 'ee/ch2-3', 'ee/ch2-4', 'ee/ch2-5', 'ee/ch2-6', 'ee/ch2-7'],
                '第3章': ['ee/ch3-1', 'ee/ch3-2', 'ee/ch3-3', 'ee/ch3-4', 'ee/ch3-5', 'ee/ch3-6', 'ee/ch3-7'],
                '第4章': ['ee/ch4-1', 'ee/ch4-2', 'ee/ch4-3', 'ee/ch4-4', 'ee/ch4-5'],
                '第5章': ['ee/ch5-1', 'ee/ch5-2', 'ee/ch5-3', 'ee/ch5-4'],
                '第6章': ['ee/ch6-1', 'ee/ch6-2', 'ee/ch6-3', 'ee/ch6-4', 'ee/ch6-5'],
                '第7章': ['ee/ch7-1', 'ee/ch7-2', 'ee/ch7-3', 'ee/ch7-4', 'ee/ch7-5', 'ee/ch7-6'],
                '第8章': ['ee/ch8-1', 'ee/ch8-2', 'ee/ch8-3', 'ee/ch8-4', 'ee/ch8-5', 'ee/ch8-6', 'ee/ch8-7']
            },
            'mw': {
                '第0章': ['mw/ch0-1'],
                '第1章': ['mw/ch1-1', 'mw/ch1-2', 'mw/ch1-3', 'mw/ch1-4'],
                '第2章': ['mw/ch2-1', 'mw/ch2-2', 'mw/ch2-3', 'mw/ch2-4', 'mw/ch2-5', 'mw/ch2-6', 'mw/ch2-7'],
                '第3章': ['mw/ch3-1', 'mw/ch3-2', 'mw/ch3-3', 'mw/ch3-4', 'mw/ch3-5'],
                '第4章': ['mw/ch4-1', 'mw/ch4-2', 'mw/ch4-3', 'mw/ch4-4', 'mw/ch4-5', 'mw/ch4-6', 'mw/ch4-7'],
                '第5章': ['mw/ch5-1', 'mw/ch5-2', 'mw/ch5-3', 'mw/ch5-4', 'mw/ch5-5', 'mw/ch5-6', 'mw/ch5-7'],
                '第6章': ['mw/ch6-1', 'mw/ch6-2', 'mw/ch6-3', 'mw/ch6-4', 'mw/ch6-5', 'mw/ch6-6', 'mw/ch6-7'],
                '第7章': ['mw/ch7-1', 'mw/ch7-2', 'mw/ch7-3', 'mw/ch7-4', 'mw/ch7-5'],
                '第8章': ['mw/ch8-1', 'mw/ch8-2', 'mw/ch8-3', 'mw/ch8-4', 'mw/ch8-5', 'mw/ch8-6']
            }
        }
        
        # 获取用户已完成的小章节ID列表
        completed_subchapters = set(
            chapter_progress_records.filter(is_completed=True)
            .values_list('chapter_id', flat=True)
        )
        
        # 调试：输出所有存储的章节ID
        all_stored_records = list(chapter_progress_records.filter(is_completed=True).values('chapter_id', 'chapter_name', 'course_code'))
        print(f"DEBUG API - 用户已完成的小章节记录: {all_stored_records}")
        print(f"DEBUG API - 已完成小章节ID集合: {completed_subchapters}")
        
        # 计算各课程的主章节完成数量
        def calculate_main_chapter_progress(course_code):
            structure = COURSE_STRUCTURE.get(course_code, {})
            total_main = len(structure)
            completed_main = 0
            
            for main_chapter, subchapters in structure.items():
                # 检查该主章节下的所有小章节是否都已完成
                completed_count = sum(1 for sub_id in subchapters if sub_id in completed_subchapters)
                is_complete = all(sub_id in completed_subchapters for sub_id in subchapters)
                
                print(f"DEBUG API - {course_code} {main_chapter}: 已完成{completed_count}/{len(subchapters)}, 是否全部完成: {is_complete}")
                
                if is_complete:
                    completed_main += 1
            
            result = {
                'completed': completed_main,
                'total': total_main,
                'rate': round(completed_main / total_main * 100, 1) if total_main > 0 else 0
            }
            print(f"DEBUG API - {course_code} 最终结果: {result}")
            return result
        
        ee_progress = calculate_main_chapter_progress('ee')
        mw_progress = calculate_main_chapter_progress('mw')
        
        return JsonResponse({
            'success': True,
            'data': {
                'ee': ee_progress,
                'mw': mw_progress,
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        print(f"获取知识学习进度失败: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': str(e),
            'data': {
                'ee': {'completed': 0, 'total': 9, 'rate': 0},
                'mw': {'completed': 0, 'total': 9, 'rate': 0}
            }
        })


@login_required
def diagnose_study_time_data(request):
    """诊断学习时间分布数据（查看数据库中各用户的记录数）"""
    from django.db.models import Count
    from .models import ChapterProgress
    
    try:
        user = request.user
        
        # 获取所有用户的练习记录统计
        all_users_practice = PracticeRecord.objects.values('user__username', 'user__id').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # 获取所有用户的知识学习记录统计
        all_users_knowledge = ChapterProgress.objects.filter(is_completed=True).values(
            'user__username', 'user__id'
        ).annotate(count=Count('id')).order_by('-count')
        
        # 当前用户的数据
        my_practice = PracticeRecord.objects.filter(user=user).count()
        my_knowledge = ChapterProgress.objects.filter(user=user, is_completed=True).count()
        
        # 计算总数
        total_practice = PracticeRecord.objects.count()
        total_knowledge = ChapterProgress.objects.filter(is_completed=True).count()
        
        return JsonResponse({
            'success': True,
            'data': {
                'current_user': {
                    'id': user.id,
                    'username': user.username,
                    'practice_records': my_practice,
                    'knowledge_records': my_knowledge,
                    'total': my_practice + my_knowledge
                },
                'all_users_practice': list(all_users_practice[:10]),  # 前10名
                'all_users_knowledge': list(all_users_knowledge[:10]),  # 前10名
                'totals': {
                    'practice_records': total_practice,
                    'knowledge_records': total_knowledge
                }
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })
