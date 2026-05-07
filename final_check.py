#!/usr/bin/env python
# -*- coding: utf-8 -*-
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject2.settings')
django.setup()

from blog.models import Question

total = Question.objects.count()
short_exp = sum(1 for q in Question.objects.all() if len((q.explanation or '').strip()) < 100)

print('=== 最终转化结果 ===\n')
print(f'总题目数: {total}')
print(f'简短解析(<100字符): {short_exp} ({short_exp/total*100:.1f}%)')
print(f'详细解析题目: {total-short_exp} ({(total-short_exp)/total*100:.1f}%)')

print('\n=== 示例解析 ===')
for q in Question.objects.all()[:3]:
    print(f'\nID{q.id}: {q.content[:50]}...')
    print(f'解析长度: {len(q.explanation or "")}字符')
    if q.explanation:
        print(f'解析预览: {q.explanation[:100]}...')
