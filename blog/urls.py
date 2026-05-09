from django.urls import path
from . import views
print("DEBUG: blog/urls.py 被加载了")

#app_name = 'blog'
urlpatterns = [
    path('', views.index, name='index'),
# 学习社区相关路由
    path('community/', views.community, name='community'),                    # 社区首页（帖子列表）
    path('community/create/', views.create_post, name='create_post'),         # 发布新问题页面
    path('community/post/<int:post_id>/', views.post_detail, name='post_detail'),  # 帖子详情页
    path('community/post/<int:post_id>/comment/', views.add_comment, name='add_comment'),  # 提交评论
    path('course/', views.course_intro, name='course_intro'),
    path('teaching-resources/', views.teaching_resources, name='teaching_resources'),  # 教学资源
# 教学资源子模块
    path('teaching-materials/', views.teaching_materials, name='teaching_materials'),
    path('simulation-platform/', views.simulation_platform, name='simulation_platform'),
    path('exercises-cases/', views.exercises_cases, name='exercises_cases'),
    path('learning-resources/', views.learning_resources, name='learning_resources'),
    path('error-notebook/', views.error_notebook, name='error_notebook'),
    # API 接口
    path('api/courses/', views.get_courses, name='api_courses'),
    path('api/chapters/', views.get_chapters, name='api_chapters'),
    path('api/questions/', views.get_questions, name='api_questions'),
    path('api/submit-answer/', views.submit_answer, name='api_submit_answer'),
    path('api/error-notebook/', views.get_error_notebook, name='api_error_notebook'),
    path('api/mark-mastered/', views.mark_as_mastered, name='api_mark_mastered'),
    path('download/<int:material_id>/', views.download_material, name='download_material'),
    path('upload-material/', views.upload_material, name='upload_material'),  # 上传资料（管理员）
    path('video/<path:filename>', views.serve_video, name='serve_video'),  # 视频流服务（支持 Range 请求）
    path('calendar/', views.calendar, name='calendar'),
    # 日历事件API（用户数据隔离）
    path('api/calendar/events/', views.get_calendar_events, name='api_calendar_events'),
    path('api/calendar/events/create/', views.create_calendar_event, name='api_calendar_create'),
    path('api/calendar/events/<int:event_id>/update/', views.update_calendar_event, name='api_calendar_update'),
    path('api/calendar/events/<int:event_id>/delete/', views.delete_calendar_event, name='api_calendar_delete'),
    path('api/calendar/auth/', views.check_calendar_auth, name='api_calendar_auth'),
    # 用户学习统计数据API
    path('api/user-stats/', views.get_user_stats, name='api_user_stats'),
    path('learning-progress/', views.learning_progress, name='learning_progress'),
    path('knowledge/', views.knowledge, name='knowledge'),
    path('knowledge/ee/', views.knowledge_ee, name='knowledge_ee'),
    path('knowledge/mw/', views.knowledge_mw, name='knowledge_mw'),
    # 章节学习进度API
    path('api/chapter-progress/', views.get_chapter_progress, name='api_chapter_progress'),
    path('api/chapter-progress/update/', views.update_chapter_progress, name='api_chapter_progress_update'),
    path('api/chapter-progress/sync/', views.sync_chapter_progress, name='api_chapter_progress_sync'),
    # 学习进度页面实时数据API
    path('api/learning-progress/knowledge/', views.get_learning_progress_knowledge, name='api_learning_progress_knowledge'),
    # 学习时间分布数据诊断API
    path('api/diagnose/study-time/', views.diagnose_study_time_data, name='api_diagnose_study_time'),
]