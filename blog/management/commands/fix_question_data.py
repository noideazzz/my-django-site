#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
题目数据修复脚本
修复发现的题型标记和答案格式问题
"""
from django.core.management.base import BaseCommand
from blog.models import Question


class Command(BaseCommand):
    help = '修复题目数据中的格式问题'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='只显示将要修改的内容，不实际执行',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        self.stdout.write("=" * 80)
        self.stdout.write(self.style.MIGRATE_HEADING("题目数据修复工具"))
        self.stdout.write("=" * 80)
        
        if dry_run:
            self.stdout.write(self.style.WARNING("\n[模拟模式] 不会实际修改数据\n"))
        
        # 1. 修复题型标记
        self.fix_question_types(dry_run)
        
        # 2. 修复判断题答案格式
        self.fix_judge_answers(dry_run)
        
        # 3. 修复选项格式
        self.fix_options_format(dry_run)
        
        self.stdout.write("\n" + "=" * 80)
        self.stdout.write(self.style.SUCCESS("修复完成！"))
        self.stdout.write("=" * 80)

    def fix_question_types(self, dry_run):
        """修复题型标记"""
        self.stdout.write("\n" + self.style.MIGRATE_HEADING("[1/3] 修复题型标记"))
        
        # 中文到代码的映射
        type_mapping = {
            '单选题': 'single',
            '多选题': 'multiple',
            '判断题': 'judge',
        }
        
        total_fixed = 0
        for chinese_type, code_type in type_mapping.items():
            count = Question.objects.filter(question_type=chinese_type).count()
            if count > 0:
                self.stdout.write(f"  发现 {count} 道题目使用 '{chinese_type}' 标记")
                if not dry_run:
                    Question.objects.filter(question_type=chinese_type).update(question_type=code_type)
                    self.stdout.write(f"  -> 已修复为 '{code_type}'")
                total_fixed += count
        
        if total_fixed == 0:
            self.stdout.write(self.style.SUCCESS("  无需修复，所有题型标记正常"))
        else:
            self.stdout.write(self.style.SUCCESS(f"  共修复 {total_fixed} 道题目"))

    def fix_judge_answers(self, dry_run):
        """修复判断题答案格式"""
        self.stdout.write("\n" + self.style.MIGRATE_HEADING("[2/3] 修复判断题答案格式"))
        
        # 查找使用 A/B 作为答案的判断题
        wrong_a = Question.objects.filter(question_type='judge', correct_answer='A')
        wrong_b = Question.objects.filter(question_type='judge', correct_answer='B')
        
        count_a = wrong_a.count()
        count_b = wrong_b.count()
        total = count_a + count_b
        
        if total > 0:
            self.stdout.write(f"  发现 {count_a} 道判断题答案为 'A' (应为 'T')")
            self.stdout.write(f"  发现 {count_b} 道判断题答案为 'B' (应为 'F')")
            
            if not dry_run:
                wrong_a.update(correct_answer='T')
                wrong_b.update(correct_answer='F')
                self.stdout.write(self.style.SUCCESS(f"  已修复 {total} 道题目"))
        else:
            self.stdout.write(self.style.SUCCESS("  判断题答案格式正常"))

    def fix_options_format(self, dry_run):
        """修复选项格式"""
        self.stdout.write("\n" + self.style.MIGRATE_HEADING("[3/3] 修复选项格式"))
        
        issues = []
        fixed_count = 0
        
        for q in Question.objects.all():
            # 检查选项是否为列表
            if not isinstance(q.options, list):
                issues.append(f"题目 {q.id}: options 不是列表")
                continue
            
            # 修复判断题选项格式
            if q.question_type == 'judge' and len(q.options) == 2:
                # 检查是否为 ["正确", "错误"] 格式
                opt1, opt2 = str(q.options[0]).strip(), str(q.options[1]).strip()
                
                # 标准化为 A/B 标签格式
                if '正确' in opt1 or '正确' in opt2:
                    new_options = ['A. 正确', 'B. 错误']
                    if not dry_run:
                        q.options = new_options
                        q.save(update_fields=['options'])
                        fixed_count += 1
        
        if fixed_count > 0:
            self.stdout.write(f"  已修复 {fixed_count} 道判断题的选项格式")
        else:
            self.stdout.write(self.style.SUCCESS("  选项格式检查完成"))
