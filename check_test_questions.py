#!/usr/bin/env python
# -*- coding: utf-8 -*-
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject2.settings')
django.setup()

from blog.models import Question
from django.db.models import Count

# 查看所有题目内容和相关信息
print('=== 题库总览 ===')
print(f'总题目数: {Question.objects.count()}')
print()

# 查找可能的测试题（内容过短或包含示例/测试字样）
print('=== 可能的测试题/示例题 ===')
test_keywords = ['测试', '示例', '示例题', '测试题', '练习', '例题']
found_test = False
for q in Question.objects.all():
    content = q.content.strip()
    if len(content) < 10 or any(kw in content for kw in test_keywords):
        found_test = True
        print(f'ID:{q.id} [{q.course.name}-{q.chapter.name}] 类型:{q.question_type} 难度:{q.difficulty}')
        print(f'  内容: {content[:80]}')
        print()

if not found_test:
    print('未找到标记为测试/示例的题目')

print()
print('=== 各章节题目数量统计 ===')
stats = Question.objects.values('chapter__name', 'course__name').annotate(count=Count('id')).order_by('course__name', 'chapter__name')
for s in stats:
    print(f"  [{s['course__name']}] {s['chapter__name']}: {s['count']}题")

print()
print('=== 显示部分题目内容示例 ===')
for q in Question.objects.all()[:10]:
    print(f'ID:{q.id} [{q.course.name}-{q.chapter.name}]')
    print(f'  题型: {q.question_type} 难度: {q.difficulty}')
    print(f'  内容: {q.content[:100]}')
    print(f'  选项: {q.options}')
    print(f'  答案: {q.correct_answer}')
    print()
