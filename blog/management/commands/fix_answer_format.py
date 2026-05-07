#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修复判断题答案格式
将A/B转换为T/F
"""
from django.core.management.base import BaseCommand
from blog.models import Question


class Command(BaseCommand):
    help = '修复判断题答案格式'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='只显示将要修改的内容，不实际执行',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        self.stdout.write("=" * 80)
        self.stdout.write(self.style.MIGRATE_HEADING("判断题答案格式修复"))
        self.stdout.write("=" * 80)

        if dry_run:
            self.stdout.write(self.style.WARNING("\n[模拟模式] 不会实际修改数据\n"))

        # 查找判断题答案格式错误的题目
        fixed_count = 0
        for q in Question.objects.filter(question_type='judge'):
            answer = q.correct_answer.strip() if q.correct_answer else ''

            if answer == 'A':
                if not dry_run:
                    q.correct_answer = 'T'
                    q.save()
                fixed_count += 1
                self.stdout.write(f"ID{q.id}: A -> T")
            elif answer == 'B':
                if not dry_run:
                    q.correct_answer = 'F'
                    q.save()
                fixed_count += 1
                self.stdout.write(f"ID{q.id}: B -> F")

        self.stdout.write("\n" + "=" * 80)
        if dry_run:
            self.stdout.write(f"[模拟完成] 可修复 {fixed_count} 道题目")
        else:
            self.stdout.write(self.style.SUCCESS(f"修复完成！共修复 {fixed_count} 道题目"))
        self.stdout.write("=" * 80)
