#!/usr/bin/env python
# -*- coding: utf-8 -*-
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject2.settings')
django.setup()

from blog.models import Question

print('=== 检查题目转化效果 ===\n')

# 检查几道题目的内容变化
print('【检查前30道题目】\n')
for q in Question.objects.all()[:30]:
    content = q.content.strip()
    # 检查是否还是占位符格式
    if '第' in content and ('判断' in content or '单选' in content or '多选' in content):
        print(f'ID{q.id}: 仍是占位符 -> {content[:50]}')
    elif len(content) < 20:
        print(f'ID{q.id}: 内容简短 -> {content}')
    else:
        print(f'ID{q.id}: 内容完整 -> {content[:60]}...')

print('\n【统计占位符题目数量】')
placeholder_count = 0
short_count = 0
for q in Question.objects.all():
    content = q.content.strip()
    if '第' in content and ('判断' in content or '单选' in content or '多选' in content):
        placeholder_count += 1
    elif len(content) < 20:
        short_count += 1

print(f'占位符题目: {placeholder_count}')
print(f'简短题目(<20字符): {short_count}')
print(f'总题目数: {Question.objects.count()}')
