#!/usr/bin/env python
# -*- coding: utf-8 -*-
import django
import os
import sys

# 设置UTF-8输出
sys.stdout.reconfigure(encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject2.settings')
django.setup()

from blog.models import Question
from django.db.models import Count

print('=== 简短题目分析（内容长度<15个字符） ===')
print()

# 按章节统计简短题目
short_questions = Question.objects.all()
chapter_stats = {}

for q in short_questions:
    content_len = len(q.content.strip())
    if content_len < 15:  # 内容少于15个字符视为测试题
        key = f"{q.course.name}-{q.chapter.name}"
        if key not in chapter_stats:
            chapter_stats[key] = {'course': q.course.name, 'chapter': q.chapter.name, 'count': 0, 'questions': []}
        chapter_stats[key]['count'] += 1
        chapter_stats[key]['questions'].append({
            'id': q.id,
            'content': q.content.strip(),
            'type': q.question_type,
            'difficulty': q.difficulty,
            'answer': q.correct_answer,
        })

# 按课程分组显示
print(f"共发现 {sum(s['count'] for s in chapter_stats.values())} 道简短题目\n")

for course in ['电磁场', '微波工程']:
    print(f"\n【{course}】")
    course_chapters = {k: v for k, v in chapter_stats.items() if v['course'] == course}
    for key, data in sorted(course_chapters.items()):
        print(f"\n  {data['chapter']}: {data['count']}题")
        for q in data['questions'][:5]:  # 只显示前5个
            print(f"    ID{q['id']}: [{q['type']}] {q['content']} -> 答案:{q['answer']}")
        if data['count'] > 5:
            print(f"    ... 还有 {data['count']-5} 题")
