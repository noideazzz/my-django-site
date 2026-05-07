#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查判断题数据完整性
"""
from django.core.management.base import BaseCommand
from django.db.models import Count
from blog.models import Question
import json


class Command(BaseCommand):
    help = '检查判断题数据完整性'

    def handle(self, *args, **options):
        self.stdout.write("=" * 80)
        self.stdout.write("判断题数据完整性检查")
        self.stdout.write("=" * 80)

        # 1. 统计判断题总数
        judge_count = Question.objects.filter(question_type='judge').count()
        self.stdout.write(f"\n[1] 判断题总数: {judge_count}")

        # 2. 检查各章节的判断题分布
        self.stdout.write("\n[2] 各章节判断题分布:")
        judge_by_chapter = Question.objects.filter(
            question_type='judge'
        ).values('course__name', 'chapter__name').annotate(
            count=Count('id')
        ).order_by('course__name', 'chapter__name')

        for item in judge_by_chapter:
            course = item['course__name'] or '未分类'
            chapter = item['chapter__name'] or '未分章节'
            count = item['count']
            self.stdout.write(f"  {course} - {chapter}: {count}道")

        # 3. 检查判断题的选项数据
        self.stdout.write("\n[3] 判断题选项数据检查:")
        
        empty_options = []
        wrong_format = []
        correct_format = []

        for q in Question.objects.filter(question_type='judge'):
            # 检查选项是否为空
            if not q.options:
                empty_options.append(q.id)
                continue

            # 检查选项格式
            if isinstance(q.options, list):
                if len(q.options) == 2:
                    correct_format.append({
                        'id': q.id,
                        'content': q.content[:50] + '...' if len(q.content) > 50 else q.content,
                        'options': q.options,
                        'answer': q.correct_answer
                    })
                else:
                    wrong_format.append({
                        'id': q.id,
                        'options': q.options,
                        'option_count': len(q.options)
                    })
            else:
                wrong_format.append({
                    'id': q.id,
                    'options': q.options,
                    'type': type(q.options).__name__
                })

        self.stdout.write(f"\n  选项数据为空的题目: {len(empty_options)}道")
        if empty_options:
            self.stdout.write(f"  题目ID: {empty_options[:20]}")

        self.stdout.write(f"\n  选项格式错误的题目: {len(wrong_format)}道")
        if wrong_format:
            self.stdout.write("  示例:")
            for item in wrong_format[:5]:
                self.stdout.write(f"    题目 {item['id']}: {item}")

        self.stdout.write(f"\n  选项格式正确的题目: {len(correct_format)}道")
        if correct_format:
            self.stdout.write("  正确格式示例:")
            for item in correct_format[:3]:
                self.stdout.write(f"    题目 {item['id']}:")
                self.stdout.write(f"      内容: {item['content']}")
                self.stdout.write(f"      选项: {item['options']}")
                self.stdout.write(f"      答案: {item['answer']}")

        # 4. 检查答案格式
        self.stdout.write("\n[4] 判断题答案格式检查:")
        valid_answers = Question.objects.filter(
            question_type='judge',
            correct_answer__in=['T', 'F', '正确', '错误']
        ).count()
        
        invalid_answers = Question.objects.filter(
            question_type='judge'
        ).exclude(
            correct_answer__in=['T', 'F', '正确', '错误']
        )

        self.stdout.write(f"  答案格式正确: {valid_answers}道")
        self.stdout.write(f"  答案格式错误: {invalid_answers.count()}道")
        
        if invalid_answers.exists():
            self.stdout.write("  错误示例:")
            for q in invalid_answers[:5]:
                self.stdout.write(f"    题目 {q.id}: 答案='{q.correct_answer}'")

        # 5. 提供修复建议
        self.stdout.write("\n" + "=" * 80)
        self.stdout.write("修复建议:")
        self.stdout.write("=" * 80)

        if empty_options:
            self.stdout.write(f"\n1. 发现 {len(empty_options)} 道判断题缺少选项数据")
            self.stdout.write("   建议为这些题目添加默认选项: ['正确', '错误']")
            
        if wrong_format:
            self.stdout.write(f"\n2. 发现 {len(wrong_format)} 道判断题选项格式异常")
            self.stdout.write("   建议修复选项格式")

        if invalid_answers.exists():
            self.stdout.write(f"\n3. 发现 {invalid_answers.count()} 道判断题答案格式错误")
            self.stdout.write("   建议将 A/B 答案转换为 T/F")
