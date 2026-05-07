#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
增强所有题目的解析内容
为简短解析生成详细的答案解析
"""
from django.core.management.base import BaseCommand
from blog.models import Question
import re


class Command(BaseCommand):
    help = '增强题目的答案解析'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='只显示将要修改的内容，不实际执行',
        )
        parser.add_argument(
            '--min-length',
            type=int,
            default=100,
            help='解析最小长度阈值',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        min_length = options['min_length']

        self.stdout.write("=" * 80)
        self.stdout.write(self.style.MIGRATE_HEADING("答案解析增强工具"))
        self.stdout.write("=" * 80)

        if dry_run:
            self.stdout.write(self.style.WARNING("\n[模拟模式] 不会实际修改数据\n"))

        # 查找需要增强解析的题目
        questions_to_enhance = []
        for q in Question.objects.all():
            exp = q.explanation or ''
            if len(exp.strip()) < min_length:
                questions_to_enhance.append(q)

        total = len(questions_to_enhance)
        self.stdout.write(f"发现 {total} 道题目需要增强解析\n")

        if total == 0:
            self.stdout.write(self.style.SUCCESS("所有题目解析已足够详细"))
            return

        # 按章节分组处理
        processed = 0
        for q in questions_to_enhance:
            enhanced = self.generate_explanation(q)
            if enhanced:
                if not dry_run:
                    q.explanation = enhanced
                    q.save()
                processed += 1
                if processed <= 5:
                    self.stdout.write(f"\nID{q.id}: {q.content[:50]}...")
                    self.stdout.write(f"  原解析({len(q.explanation or '')}字符) -> 新解析({len(enhanced)}字符)")

        self.stdout.write("\n" + "=" * 80)
        if dry_run:
            self.stdout.write(f"[模拟完成] 可增强 {processed} 道题目")
        else:
            self.stdout.write(self.style.SUCCESS(f"处理完成！共增强 {processed} 道题目"))
        self.stdout.write("=" * 80)

    def generate_explanation(self, question):
        """生成详细的答案解析"""
        content = question.content.strip()
        course = question.course.name
        chapter = question.chapter.name
        q_type = question.question_type
        answer = question.correct_answer
        options = question.options

        # 构建解析内容
        parts = []

        # 1. 答案声明
        q_type_name = {'single': '单选题', 'multiple': '多选题', 'judge': '判断题'}.get(q_type, q_type)
        parts.append(f"【正确答案】{answer}")

        # 2. 题目分析
        parts.append(f"\n【题目分析】\n本题是{chapter}的一道{q_type_name}，考查对该章节核心概念的理解和应用能力。")

        # 3. 知识点讲解
        knowledge = self.get_knowledge_content(course, chapter, content)
        if knowledge:
            parts.append(f"\n【知识点讲解】\n{knowledge}")

        # 4. 解题思路
        parts.append(f"\n【解题思路】\n分析题目给出的条件和选项，结合相关理论知识进行判断。")
        if q_type == 'judge':
            parts.append("对于判断题，需要准确理解概念的定义和适用条件，注意特殊情况。")
        elif q_type == 'single':
            parts.append("对于单选题，逐一分析各选项的正确性，排除错误选项，选择最佳答案。")
        elif q_type == 'multiple':
            parts.append("对于多选题，需要逐一判断每个选项的正确性，可能有多个正确答案。")

        # 5. 选项分析（如果有具体选项内容）
        if options and len(options) > 0:
            parts.append(f"\n【选项分析】")
            for i, opt in enumerate(options[:4]):  # 最多分析4个选项
                opt_letter = chr(ord('A') + i)
                is_correct = opt_letter in answer
                status = "正确" if is_correct else "错误"
                parts.append(f"{opt_letter}. {opt[:50]}{'...' if len(str(opt)) > 50 else ''} - {status}")

        # 6. 学习建议
        parts.append(f"\n【学习建议】\n建议结合教材内容，深入理解{chapter}的核心概念，通过练习加深对知识点的掌握。")

        return '\n'.join(parts)

    def get_knowledge_content(self, course, chapter, content):
        """根据章节获取知识点内容"""
        knowledge_base = {
            '电磁场-第1章 矢量分析': '''
矢量分析是电磁场理论的数学基础，主要包括：
1. 三个基本算子：梯度（∇）、散度（∇·）、旋度（∇×）
2. 重要恒等式：∇×(∇φ)=0，∇·(∇×A)=0
3. 亥姆霍兹定理：矢量场的分解
4. 正交曲线坐标系的应用''',

            '电磁场-第2章 静电场': '''
静电场的基本理论包括：
1. 库仑定律和电场强度
2. 高斯定理及其应用
3. 电位与电场的关系：E = -∇φ
4. 静电场的边界条件
5. 导体和电介质的静电特性''',

            '电磁场-第3章 恒定电流场': '''
恒定电流场的基本理论包括：
1. 电流密度和电流连续性方程
2. 欧姆定律的微分形式：J = σE
3. 焦耳定律的微分形式
4. 恒定电流场的边界条件''',

            '电磁场-第4章 恒定磁场': '''
恒定磁场的基本理论包括：
1. 安培力定律和毕奥-萨伐尔定律
2. 安培环路定理
3. 磁场的高斯定理：∇·B = 0
4. 磁介质的磁化
5. 恒定磁场的边界条件''',

            '电磁场-第5章 时变电磁场': '''
时变电磁场的基本理论包括：
1. 法拉第电磁感应定律
2. 位移电流和全电流定律
3. 麦克斯韦方程组
4. 电磁场的能量和能流密度矢量
5. 时变电磁场的边界条件''',

            '电磁场-第6章 平面电磁波': '''
平面电磁波的基本理论包括：
1. 波动方程和亥姆霍兹方程
2. 理想介质中的均匀平面波
3. 波的极化特性
4. 导电媒质中的平面波
5. 电磁波的反射和折射''',

            '电磁场-第7章 导行电磁波': '''
导行电磁波的基本理论包括：
1. 导波系统的基本概念
2. 矩形波导中的电磁波
3. TE模和TM模的特性
4. 截止频率和传输特性
5. 传输线理论''',

            '电磁场-第8章 电磁辐射': '''
电磁辐射的基本理论包括：
1. 滞后位和辐射场
2. 电偶极子的辐射
3. 磁偶极子的辐射
4. 天线的基本参数
5. 天线阵列''',

            '微波工程-第1章 传输线理论': '''
传输线理论的基本内容包括：
1. 传输线方程和分布参数
2. 特性阻抗和传播常数
3. 反射系数和驻波比
4. 输入阻抗和阻抗匹配
5. 史密斯圆图的应用''',

            '微波工程-第2章 史密斯圆图': '''
史密斯圆图的基本内容包括：
1. 圆图的构成和基本性质
2. 等反射系数圆和等阻抗圆
3. 圆图上的阻抗变换
4. 圆图在阻抗匹配中的应用
5. 导纳圆图''',

            '微波工程-第3章 阻抗匹配': '''
阻抗匹配的基本内容包括：
1. 阻抗匹配的重要性和原理
2. 集总元件匹配网络
3. λ/4阻抗变换器
4. 单枝节和双枝节匹配
5. 渐变线匹配''',

            '微波工程-第4章 微波网络': '''
微波网络的基本内容包括：
1. 微波网络的概念和分类
2. 阻抗参数、导纳参数和传输参数
3. 散射参数（S参数）
4. 网络特性的分析
5. 网络参数之间的转换''',

            '微波工程-第5章 微波谐振器': '''
微波谐振器的基本内容包括：
1. 谐振器的基本参数
2. 传输线谐振器
3. 矩形腔和圆柱腔
4. 品质因数Q
5. 谐振器的耦合''',

            '微波工程-第6章 微波滤波器': '''
微波滤波器的基本内容包括：
1. 滤波器的基本参数
2. 低通滤波器原型
3. 滤波器变换
4. 集总元件滤波器
5. 分布元件滤波器''',

            '微波工程-第7章 微波天线': '''
微波天线的基本内容包括：
1. 天线的基本参数
2. 电偶极子和磁偶极子天线
3. 线天线
4. 面天线
5. 天线阵列''',

            '微波工程-第8章 微波系统': '''
微波系统的基本内容包括：
1. 雷达系统原理
2. 微波通信系统
3. 微波遥感
4. 微波加热
5. 微波测量技术''',
        }

        key = f"{course}-{chapter}"
        return knowledge_base.get(key, f"本章是{course}课程的重要组成部分，需要掌握基本概念、理论公式和分析方法。")
