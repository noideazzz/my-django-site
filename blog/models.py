from django.db import models
from django.conf import settings
import os


class Post(models.Model):
    """社区帖子模型"""
    CHAPTER_CHOICES = [
        ('general', '综合讨论'),
        ('vector', '矢量分析基础'),
        ('electrostatic', '静电场'),
        ('magnetostatic', '恒定磁场'),
        ('maxwell', '麦克斯韦方程组'),
        ('wave', '平面电磁波'),
        ('transmission', '传输线理论'),
        ('waveguide', '波导与谐振腔'),
        ('antenna', '天线原理'),
        ('microwave', '微波网络'),
        ('experiment', '实验答疑'),
    ]

    title = models.CharField('问题标题', max_length=200)
    content = models.TextField('问题内容')
    author = models.CharField('提问者', max_length=50)
    chapter = models.CharField('所属章节', max_length=20, choices=CHAPTER_CHOICES, default='general')
    created_at = models.DateTimeField(auto_now_add=True)
    views = models.PositiveIntegerField('浏览量', default=0)
    likes = models.PositiveIntegerField('点赞数', default=0)

    class Meta:
        db_table = 'community_posts'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Comment(models.Model):
    """评论模型"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField('回复内容')
    author = models.CharField('回复者', max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    is_teacher = models.BooleanField('教师回复', default=False)

    class Meta:
        db_table = 'community_comments'
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author} on {self.post.title}"


class Course(models.Model):
    """课程模型"""
    name = models.CharField('课程名称', max_length=50)
    code = models.CharField('课程代码', max_length=20, unique=True)
    description = models.TextField('课程描述', blank=True)

    class Meta:
        verbose_name = '课程'
        verbose_name_plural = '课程管理'

    def __str__(self):
        return self.name


class Chapter(models.Model):
    """章节模型（每门课程有自己的章节）"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='chapters', verbose_name='所属课程')
    name = models.CharField('章节名称', max_length=100)
    code = models.CharField('章节代码', max_length=20)
    order = models.IntegerField('排序', default=0)

    def __str__(self):
        return f"[{self.course.name}] {self.name}"

    class Meta:
        verbose_name = '章节'
        verbose_name_plural = '章节管理'
        ordering = ['course', 'order']
        unique_together = ['course', 'code']


class Question(models.Model):
    """题目模型"""
    QUESTION_TYPES = [
        ('single', '单选题'),
        ('multiple', '多选题'),
        ('judge', '判断题'),
    ]

    DIFFICULTY_LEVELS = [
        (1, '简单'),
        (2, '中等'),
        (3, '困难'),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='questions', verbose_name='所属课程')
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='questions', verbose_name='所属章节')
    question_type = models.CharField('题型', max_length=10, choices=QUESTION_TYPES, default='single')
    difficulty = models.IntegerField('难度', choices=DIFFICULTY_LEVELS, default=1)
    content = models.TextField('题目内容')
    options = models.JSONField('选项', default=list, help_text='选项列表，如 ["A. xxx", "B. xxx"]')
    correct_answer = models.CharField('正确答案', max_length=10, help_text='单选填A/B/C/D，多选填AB/ACD等，判断填T/F')
    explanation = models.TextField('答案解析')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    is_active = models.BooleanField('是否启用', default=True)

    class Meta:
        verbose_name = '题目'
        verbose_name_plural = '题目管理'
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.course.name}-{self.chapter.name}] {self.content[:50]}..."


class PracticeRecord(models.Model):
    """练习记录"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='用户')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name='题目')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name='课程')
    user_answer = models.CharField('用户答案', max_length=10)
    is_correct = models.BooleanField('是否正确')
    practice_time = models.DateTimeField('练习时间', auto_now_add=True)

    class Meta:
        verbose_name = '练习记录'
        verbose_name_plural = '练习记录'


class ErrorNotebook(models.Model):
    """错题本（按课程分类）"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='error_notes',
                             verbose_name='用户')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name='课程')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name='错题')
    error_count = models.IntegerField('错误次数', default=1)
    last_error_time = models.DateTimeField('最后错误时间', auto_now=True)
    is_mastered = models.BooleanField('是否已掌握', default=False)

    class Meta:
        verbose_name = '错题记录'
        verbose_name_plural = '错题本'
        unique_together = ['user', 'question']


def course_file_path(instance, filename):
    """自定义文件上传路径"""
    course_code = instance.course.code if instance.course else 'other'
    chapter_code = instance.chapter.code if instance.chapter else 'general'
    import time
    timestamp = int(time.time())
    name, ext = os.path.splitext(filename)
    new_filename = f"{timestamp}_{name}{ext}"
    return f'course_files/{course_code}/{chapter_code}/{new_filename}'


class CourseMaterial(models.Model):
    """课程资料模型"""
    FILE_TYPES = [
        ('ppt', 'PPT课件'),
        ('pdf', 'PDF文档'),
        ('video', '视频'),
        ('code', '代码/程序'),
        ('data', '数据文件'),
        ('other', '其他'),
    ]

    title = models.CharField('资料标题', max_length=200)
    description = models.TextField('资料描述', blank=True)
    file = models.FileField('文件', upload_to=course_file_path)
    file_size = models.BigIntegerField('文件大小(字节)', default=0)
    file_type = models.CharField('文件类型', max_length=10, choices=FILE_TYPES, default='other')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='materials', verbose_name='所属课程')
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, null=True, blank=True, related_name='materials',
                                verbose_name='所属章节')
    is_public = models.BooleanField('是否公开', default=True)
    require_login = models.BooleanField('需要登录', default=True)
    download_count = models.IntegerField('下载次数', default=0)
    upload_time = models.DateTimeField('上传时间', auto_now_add=True)
    uploader = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='上传者')

    class Meta:
        verbose_name = '课程资料'
        verbose_name_plural = '课程资料管理'
        ordering = ['-upload_time']

    def __str__(self):
        return f"[{self.course.name}] {self.title}"

    def save(self, *args, **kwargs):
        if self.file and not self.file_size:
            self.file_size = self.file.size
            ext = os.path.splitext(self.file.name)[1].lower()
            type_map = {
                '.ppt': 'ppt', '.pptx': 'ppt',
                '.pdf': 'pdf',
                '.mp4': 'video', '.avi': 'video', '.mkv': 'video',
                '.py': 'code', '.m': 'code', '.ipynb': 'code',
                '.csv': 'data', '.txt': 'data', '.dat': 'data',
            }
            self.file_type = type_map.get(ext, 'other')
        super().save(*args, **kwargs)

    def get_file_size_display(self):
        size = self.file_size
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        elif size < 1024 * 1024 * 1024:
            return f"{size / (1024 * 1024):.1f} MB"
        else:
            return f"{size / (1024 * 1024 * 1024):.1f} GB"


class DownloadRecord(models.Model):
    """下载记录"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='用户')
    material = models.ForeignKey(CourseMaterial, on_delete=models.CASCADE, related_name='downloads',
                                 verbose_name='资料')
    download_time = models.DateTimeField('下载时间', auto_now_add=True)
    ip_address = models.GenericIPAddressField('IP地址', null=True, blank=True)

    class Meta:
        verbose_name = '下载记录'
        verbose_name_plural = '下载记录'
        ordering = ['-download_time']


class CalendarEvent(models.Model):
    """用户日历事件模型 - 实现用户数据隔离"""
    EVENT_TYPES = [
        ('theory', '理论课'),
        ('lab', '实验课'),
        ('exam', '考试'),
        ('assignment', '作业'),
        ('review', '复习'),
        ('other', '其他'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='calendar_events',
        verbose_name='用户'
    )
    title = models.CharField('事件标题', max_length=200)
    date = models.DateField('日期')
    time = models.TimeField('时间', null=True, blank=True)
    location = models.CharField('地点', max_length=200, blank=True)
    event_type = models.CharField('事件类型', max_length=20, choices=EVENT_TYPES, default='other')
    description = models.TextField('描述', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '日历事件'
        verbose_name_plural = '日历事件管理'
        ordering = ['-date', '-time']
        indexes = [
            models.Index(fields=['user', 'date']),
        ]

    def __str__(self):
        return f"[{self.user.username}] {self.title} ({self.date})"


class ChapterProgress(models.Model):
    """章节学习进度（用于知识学习页面标记完成状态）"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chapter_progress_records',
        verbose_name='用户'
    )
    chapter_id = models.CharField('章节ID', max_length=50, help_text='格式：course_code/chapter_code，如 ee/ch1')
    chapter_name = models.CharField('章节名称', max_length=100)
    course_code = models.CharField('课程代码', max_length=20, help_text='ee=电磁场, mw=微波工程')
    is_completed = models.BooleanField('是否已完成', default=False)
    completed_at = models.DateTimeField('完成时间', null=True, blank=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    # 子任务进度字段
    completed_subtasks_count = models.PositiveIntegerField('已完成子任务数', default=0)
    total_subtasks_count = models.PositiveIntegerField('总子任务数', default=0)
    subtasks = models.JSONField('子任务进度', default=dict, blank=True, help_text='存储各学习小点的完成状态')

    class Meta:
        verbose_name = '章节学习进度'
        verbose_name_plural = '章节学习进度管理'
        unique_together = ['user', 'chapter_id']
        ordering = ['-completed_at', '-updated_at']

    def __str__(self):
        status = '已完成' if self.is_completed else '学习中'
        return f"[{self.user.username}] {self.chapter_name} ({status})"
