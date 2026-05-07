#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

"""
from django.core.management.base import BaseCommand
from django.db.models import Count, Q
from blog.models import Question, Course, Chapter
import json


class Command(BaseCommand):
    help = ''

    def handle(self, *args, **options):
        self.stdout.write("=" * 80)
        self.stdout.write(self.style.SUCCESS(""))
        self.stdout.write("=" * 80)
        
        # 1. 
        self.check_total_count()
        
        # 2. 
        self.check_type_distribution()
        
        # 3. 
        self.check_difficulty_distribution()
        
        # 4. 
        self.check_course_chapter_distribution()
        
        # 5. 
        self.check_data_integrity()
        
        # 6. 
        self.check_duplicates()
        
        # 7. 
        self.check_options_format()
        
        # 8. 
        self.check_answer_format()
        
        self.stdout.write("\n" + "=" * 80)
        self.stdout.write(self.style.SUCCESS(""))
        self.stdout.write("=" * 80)

    def check_total_count(self):
        """1. """
        self.stdout.write("\n" + self.style.MIGRATE_HEADING("[1. ]"))
        
        total = Question.objects.count()
        active = Question.objects.filter(is_active=True).count()
        inactive = Question.objects.filter(is_active=False).count()
        
        self.stdout.write(f"  : {total}")
        self.stdout.write(f"  - : {active}")
        self.stdout.write(f"  - : {inactive}")
        
        if total == 0:
            self.stdout.write(self.style.ERROR("  [] "))
        elif total < 50:
            self.stdout.write(self.style.WARNING("  [] , 50 "))
        else:
            self.stdout.write(self.style.SUCCESS(f"  [OK]  ({total} )"))

    def check_type_distribution(self):
        """2. """
        self.stdout.write("\n" + self.style.MIGRATE_HEADING("[2. ]"))
        
        type_stats = Question.objects.values('question_type').annotate(
            count=Count('id')
        ).order_by('question_type')
        
        type_names = {
            'single': '',
            'multiple': '',
            'judge': ''
        }
        
        total = Question.objects.count()
        
        for stat in type_stats:
            q_type = stat['question_type']
            count = stat['count']
            percentage = (count / total * 100) if total > 0 else 0
            name = type_names.get(q_type, f'({q_type})')
            self.stdout.write(f"  {name}: {count}  ({percentage:.1f}%)")
        
        # 
        counts = [s['count'] for s in type_stats]
        if counts:
            min_count, max_count = min(counts), max(counts)
            if max_count > 0 and min_count / max_count < 0.1:
                self.stdout.write(self.style.WARNING(
                    f"  [] , {min_count} , {max_count} "
                ))
            else:
                self.stdout.write(self.style.SUCCESS("  [OK] "))

    def check_difficulty_distribution(self):
        """3. """
        self.stdout.write("\n" + self.style.MIGRATE_HEADING("[3. ]"))
        
        difficulty_stats = Question.objects.values('difficulty').annotate(
            count=Count('id')
        ).order_by('difficulty')
        
        difficulty_names = {
            1: '',
            2: '',
            3: ''
        }
        
        total = Question.objects.count()
        
        for stat in difficulty_stats:
            level = stat['difficulty']
            count = stat['count']
            percentage = (count / total * 100) if total > 0 else 0
            name = difficulty_names.get(level, f'({level})')
            self.stdout.write(f"  {name}: {count}  ({percentage:.1f}%)")
        
        # 
        diff_list = list(difficulty_stats)
        if len(diff_list) >= 3:
            easy = next((s['count'] for s in diff_list if s['difficulty'] == 1), 0)
            medium = next((s['count'] for s in diff_list if s['difficulty'] == 2), 0)
            hard = next((s['count'] for s in diff_list if s['difficulty'] == 3), 0)
            
            if easy == 0 or medium == 0 or hard == 0:
                self.stdout.write(self.style.WARNING("  [] : "))
            elif hard < total * 0.1:
                self.stdout.write(self.style.WARNING("  [] : ,"))
            else:
                self.stdout.write(self.style.SUCCESS("  [OK] "))

    def check_course_chapter_distribution(self):
        """4. """
        self.stdout.write("\n" + self.style.MIGRATE_HEADING("[4. ]"))
        
        # 
        course_stats = Question.objects.values(
            'course__name', 'course__code'
        ).annotate(
            count=Count('id')
        ).order_by('-count')
        
        self.stdout.write("  :")
        for stat in course_stats:
            name = stat['course__name'] or ''
            code = stat['course__code'] or 'N/A'
            count = stat['count']
            self.stdout.write(f"    - {name} ({code}): {count} ")
        
        # 
        chapter_stats = Question.objects.values(
            'course__name', 'chapter__name'
        ).annotate(
            count=Count('id')
        ).order_by('course__name', 'chapter__name')
        
        self.stdout.write("\n  :")
        current_course = None
        for stat in chapter_stats:
            course_name = stat['course__name'] or ''
            chapter_name = stat['chapter__name'] or ''
            count = stat['count']
            
            if course_name != current_course:
                self.stdout.write(f"\n    [{course_name}]")
                current_course = course_name
            
            self.stdout.write(f"      - {chapter_name}: {count} ")
            
            if count < 3:
                self.stdout.write(self.style.WARNING(
                    f"        [] "
                ))

    def check_data_integrity(self):
        """5. """
        self.stdout.write("\n" + self.style.MIGRATE_HEADING("[5. ]"))
        
        issues = []
        
        # 
        empty_content = Question.objects.filter(
            Q(content__isnull=True) | Q(content='')
        ).count()
        if empty_content > 0:
            issues.append(f"  [] : {empty_content} ")
        
        # 
        empty_options = Question.objects.filter(
            Q(options__isnull=True) | Q(options=[])
        ).count()
        if empty_options > 0:
            issues.append(f"  [] : {empty_options} ")
        
        # 
        empty_answer = Question.objects.filter(
            Q(correct_answer__isnull=True) | Q(correct_answer='')
        ).count()
        if empty_answer > 0:
            issues.append(f"  [] : {empty_answer} ")
        
        # 
        empty_explanation = Question.objects.filter(
            Q(explanation__isnull=True) | Q(explanation='')
        ).count()
        if empty_explanation > 0:
            issues.append(f"  [] : {empty_explanation} ")
        
        # 
        no_course = Question.objects.filter(course__isnull=True).count()
        if no_course > 0:
            issues.append(f"  [] : {no_course} ")
        
        # 
        no_chapter = Question.objects.filter(chapter__isnull=True).count()
        if no_chapter > 0:
            issues.append(f"  [] : {no_chapter} ")
        
        if issues:
            self.stdout.write(self.style.ERROR(":"))
            for issue in issues:
                self.stdout.write(self.style.ERROR(issue))
        else:
            self.stdout.write(self.style.SUCCESS("  [OK] "))

    def check_duplicates(self):
        """6. """
        self.stdout.write("\n" + self.style.MIGRATE_HEADING("[6. ]"))
        
        # 
        from django.db.models import Func, F
        
        duplicates = Question.objects.values('content').annotate(
            count=Count('id')
        ).filter(count__gt=1)
        
        if duplicates.exists():
            self.stdout.write(self.style.WARNING(
                f"  []  {duplicates.count()} "
            ))
            for dup in duplicates[:5]:  # 5
                self.stdout.write(f"    -  {dup['count']} : {dup['content'][:50]}...")
        else:
            self.stdout.write(self.style.SUCCESS("  [OK] "))

    def check_options_format(self):
        """7. """
        self.stdout.write("\n" + self.style.MIGRATE_HEADING("[7. ]"))
        
        issues = []
        questions_with_issues = []
        
        for q in Question.objects.all():
            # 
            if not isinstance(q.options, list):
                issues.append(f" {q.id}: options ")
                questions_with_issues.append(q.id)
                continue
            
            # 
            option_count = len(q.options)
            
            if q.question_type == 'judge':
                # 2
                if option_count != 2:
                    issues.append(f" {q.id} (): 2,{option_count}")
                    questions_with_issues.append(q.id)
            elif q.question_type in ['single', 'multiple']:
                # 4
                if option_count < 2:
                    issues.append(f" {q.id} ():  ({option_count})")
                    questions_with_issues.append(q.id)
                elif option_count > 6:
                    issues.append(f" {q.id}:  ({option_count})")
                    questions_with_issues.append(q.id)
            
            # 
            for i, opt in enumerate(q.options):
                if not opt or str(opt).strip() == '':
                    issues.append(f" {q.id}:  {i+1} ")
                    if q.id not in questions_with_issues:
                        questions_with_issues.append(q.id)
        
        if issues:
            self.stdout.write(self.style.WARNING(f"  []  {len(issues)} :"))
            for issue in issues[:10]:  # 10
                self.stdout.write(f"    - {issue}")
            if len(issues) > 10:
                self.stdout.write(f"    ...  {len(issues) - 10} ")
            
            self.stdout.write(f"\n   ID: {questions_with_issues[:20]}")
        else:
            self.stdout.write(self.style.SUCCESS("  [OK] "))

    def check_answer_format(self):
        """8. """
        self.stdout.write("\n" + self.style.MIGRATE_HEADING("[8. ]"))
        
        issues = []
        
        for q in Question.objects.all():
            answer = q.correct_answer
            
            if not answer:
                continue
            
            if q.question_type == 'single':
                # 
                if len(answer) != 1 or answer not in 'ABCDEF':
                    issues.append(f" {q.id} ():  '{answer}'")
            
            elif q.question_type == 'multiple':
                # 
                if len(answer) < 2:
                    issues.append(f" {q.id} ():  '{answer}'")
                else:
                    # 
                    for char in answer:
                        if char not in 'ABCDEF':
                            issues.append(f" {q.id} ():  '{char}'")
                            break
            
            elif q.question_type == 'judge':
                #  T  F
                if answer not in ['T', 'F', '', '']:
                    issues.append(f" {q.id} ():  '{answer}', T/F  /")
        
        if issues:
            self.stdout.write(self.style.WARNING(f"  []  {len(issues)} :"))
            for issue in issues[:10]:
                self.stdout.write(f"    - {issue}")
            if len(issues) > 10:
                self.stdout.write(f"    ...  {len(issues) - 10} ")
        else:
            self.stdout.write(self.style.SUCCESS("  [OK] "))
