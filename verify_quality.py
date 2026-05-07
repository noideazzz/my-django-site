#!/usr/bin/env python
# -*- coding: utf-8 -*-
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject2.settings')
django.setup()

from blog.models import Question

print('=== 习题质量检查 ===\n')

# 统计指标
total = Question.objects.count()
short_content = 0  # 内容少于30字符
short_exp = 0      # 解析少于50字符
placeholder = 0    # 占位符

# 按章节统计
chapter_stats = {}

for q in Question.objects.all():
    content = q.content.strip()
    exp = (q.explanation or '').strip()

    # 统计
    if len(content) < 30:
        short_content += 1
    if len(exp) < 50:
        short_exp += 1
    if '第' in content and ('判断' in content or '单选' in content or '多选' in content):
        placeholder += 1

    # 章节统计
    key = f"{q.course.name}-{q.chapter.name}"
    if key not in chapter_stats:
        chapter_stats[key] = {'total': 0, 'short': 0}
    chapter_stats[key]['total'] += 1
    if len(content) < 50 or len(exp) < 50:
        chapter_stats[key]['short'] += 1

print(f'总题目数: {total}')
print(f'简短内容(<30字符): {short_content} ({short_content/total*100:.1f}%)')
print(f'简短解析(<50字符): {short_exp} ({short_exp/total*100:.1f}%)')
print(f'占位符题目: {placeholder}')

print('\n=== 各章节质量统计 ===')
for key, stats in sorted(chapter_stats.items()):
    quality = stats['short'] / stats['total'] * 100
    status = '✓' if quality < 20 else '⚠' if quality < 50 else '✗'
    print(f'{status} {key}: {stats["short"]}/{stats["total"]} ({quality:.0f}%)')

print('\n=== 示例题目（前5道） ===')
for q in Question.objects.all()[:5]:
    print(f'\nID{q.id} [{q.course.name}-{q.chapter.name}] {q.question_type}')
    print(f'题目: {q.content[:80]}...')
    print(f'解析({len(q.explanation or "")}字符): {(q.explanation or "无")[:80]}...')
