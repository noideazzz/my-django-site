#!/usr/bin/env python
# -*- coding: utf-8 -*-
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject2.settings')
django.setup()

from blog.models import Question

print('=== 未匹配的简短题目示例（前50道）===\n')

# 获取简短题目
short_questions = []
for q in Question.objects.all():
    content_len = len(q.content.strip())
    explanation_len = len(q.explanation.strip()) if q.explanation else 0
    if content_len < 20 or explanation_len < 15:
        short_questions.append({
            'id': q.id,
            'course': q.course.name,
            'chapter': q.chapter.name,
            'content': q.content.strip(),
            'type': q.question_type,
            'options': q.options
        })

# 按章节分组显示前30道
count = 0
for q in short_questions[:30]:
    print(f"[{q['course']}-{q['chapter']}]")
    print(f"  ID{q['id']} [{q['type']}]: {q['content']}")
    if len(str(q['options'])) < 100:
        print(f"  选项: {q['options']}")
    else:
        print(f"  选项: {str(q['options'])[:80]}...")
    print()
    count += 1

print(f"\n共显示 {count} 道未匹配题目，总计 {len(short_questions)} 道")
