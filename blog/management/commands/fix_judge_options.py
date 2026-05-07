#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修复判断题选项数据
为缺少选项的判断题添加默认选项
"""
from django.core.management.base import BaseCommand
from blog.models import Question


class Command(BaseCommand):
    help = '修复判断题选项数据'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='只显示将要修改的内容，不实际执行',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        self.stdout.write("=" * 80)
        self.stdout.write("判断题选项数据修复工具")
        self.stdout.write("=" * 80)
        
        if dry_run:
            self.stdout.write("\n[模拟模式] 不会实际修改数据\n")
        
        # 查找缺少选项的判断题
        judge_without_options = Question.objects.filter(
            question_type='judge'
        ).filter(
            options__isnull=True
        ) | Question.objects.filter(
            question_type='judge'
        ).filter(
            options=[]
        )
        
        count = judge_without_options.count()
        
        self.stdout.write(f"\n发现 {count} 道判断题缺少选项数据")
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS("\n所有判断题选项数据正常！"))
            return
        
        # 显示部分示例
        self.stdout.write("\n示例题目:")
        for q in judge_without_options[:5]:
            self.stdout.write(f"  题目 {q.id}: {q.content[:50]}...")
            self.stdout.write(f"    当前选项: {q.options}")
        
        if not dry_run:
            # 执行修复
            fixed_count = 0
            for q in judge_without_options:
                # 为判断题添加默认选项
                q.options = ['A. 正确', 'B. 错误']
                q.save(update_fields=['options'])
                fixed_count += 1
            
            self.stdout.write(self.style.SUCCESS(f"\n成功修复 {fixed_count} 道判断题！"))
            self.stdout.write("已为这些题目添加默认选项: ['A. 正确', 'B. 错误']")
        else:
            self.stdout.write(f"\n[模拟] 将修复 {count} 道题目")
            self.stdout.write("[模拟] 将添加默认选项: ['A. 正确', 'B. 错误']")
        
        self.stdout.write("\n" + "=" * 80)
