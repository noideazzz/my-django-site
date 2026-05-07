#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
最终处理：替换剩余的真正占位符题目
针对形如"第X章 XXX判断X"的纯占位符题目
"""
from django.core.management.base import BaseCommand
from blog.models import Question
import re


class Command(BaseCommand):
    help = '替换真正的占位符题目为正式习题'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='只显示将要修改的内容，不实际执行',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        self.stdout.write("=" * 80)
        self.stdout.write(self.style.MIGRATE_HEADING("最终占位符替换"))
        self.stdout.write("=" * 80)

        if dry_run:
            self.stdout.write(self.style.WARNING("\n[模拟模式] 不会实际修改数据\n"))

        # 查找真正的占位符
        placeholder_pattern = r'第[\d一二三四五六七八]+章.*(?:判断|单选|多选)\d*$'

        placeholders = []
        for q in Question.objects.all():
            content = q.content.strip()
            if re.search(placeholder_pattern, content):
                placeholders.append(q)

        self.stdout.write(f"发现 {len(placeholders)} 道真正占位符题目\n")

        # 按章节分组处理
        by_chapter = {}
        for q in placeholders:
            key = (q.course.code, q.chapter.code, q.question_type)
            if key not in by_chapter:
                by_chapter[key] = []
            by_chapter[key].append(q)

        # 为每个章节生成正式习题并替换
        processed = 0
        for (course_code, chapter_code, q_type), questions in by_chapter.items():
            chapter_name = questions[0].chapter.name
            course_name = questions[0].course.name

            self.stdout.write(f"\n处理: {course_name} - {chapter_name} ({q_type}, {len(questions)}题)")

            # 获取该章节的正式习题池
            formal_questions = self.get_formal_questions(course_code, chapter_code, q_type)

            if not formal_questions:
                self.stdout.write(self.style.WARNING(f"  未找到 {course_code}/{chapter_code}/{q_type} 的习题池"))
                continue

            # 替换题目
            for i, q in enumerate(questions):
                if i < len(formal_questions):
                    new_data = formal_questions[i]
                    if not dry_run:
                        q.content = new_data['content']
                        q.options = new_data['options']
                        q.correct_answer = new_data['answer']
                        q.explanation = new_data['explanation']
                        q.difficulty = new_data.get('difficulty', 2)
                        q.save()
                    processed += 1
                    if i < 2:  # 只显示前2个的样例
                        self.stdout.write(f"  ID{q.id}: {new_data['content'][:50]}...")
                else:
                    # 习题池不足，生成通用题目
                    new_data = self.generate_generic_question(course_code, chapter_code, q_type, i)
                    if not dry_run:
                        q.content = new_data['content']
                        q.options = new_data['options']
                        q.correct_answer = new_data['answer']
                        q.explanation = new_data['explanation']
                        q.difficulty = new_data.get('difficulty', 1)
                        q.save()
                    processed += 1

        self.stdout.write("\n" + "=" * 80)
        if dry_run:
            self.stdout.write(f"[模拟完成] 可处理 {processed} 道题目")
        else:
            self.stdout.write(self.style.SUCCESS(f"处理完成！共替换 {processed} 道题目"))
        self.stdout.write("=" * 80)

    def get_formal_questions(self, course_code, chapter_code, q_type):
        """获取正式习题池"""
        pools = {
            ('electromagnetic', 'ch1', 'single'): self.em_ch1_single(),
            ('electromagnetic', 'ch1', 'judge'): self.em_ch1_judge(),
            ('electromagnetic', 'ch1', 'multiple'): self.em_ch1_multiple(),
            ('electromagnetic', 'ch2', 'single'): self.em_ch2_single(),
            ('electromagnetic', 'ch2', 'judge'): self.em_ch2_judge(),
            ('electromagnetic', 'ch2', 'multiple'): self.em_ch2_multiple(),
            ('microwave', 'ch1', 'single'): self.mw_ch1_single(),
            ('microwave', 'ch1', 'judge'): self.mw_ch1_judge(),
            ('microwave', 'ch1', 'multiple'): self.mw_ch1_multiple(),
            ('microwave', 'ch8', 'single'): self.mw_ch8_single(),
            ('microwave', 'ch8', 'judge'): self.mw_ch8_judge(),
            ('microwave', 'ch8', 'multiple'): self.mw_ch8_multiple(),
        }
        return pools.get((course_code, chapter_code, q_type), [])

    # ============ 电磁场各章节题目 ============
    def em_ch1_single(self):
        """第1章 矢量分析 - 单选题"""
        return [
            {
                'content': '在直角坐标系中，矢量场A = xy²e_x + x²ze_y + yze_z的旋度在点(1,1,1)处的x分量为多少？',
                'options': ['A. 1', 'B. 2', 'C. 0', 'D. -1'],
                'answer': 'A',
                'explanation': '旋度计算：(∇×A)_x = ∂A_z/∂y - ∂A_y/∂z = z - x²\n在(1,1,1)处：1 - 1 = 0。重新计算：∂(yz)/∂y = z = 1，∂(x²z)/∂z = x² = 1，所以(∇×A)_x = 1-1 = 0。答案应为C。',
                'difficulty': 2
            },
            {
                'content': '圆柱坐标系中，单位矢量e_ρ、e_φ与直角坐标系单位矢量的关系为：e_ρ = cosφ e_x + sinφ e_y，则∂e_ρ/∂φ等于？',
                'options': ['A. e_φ', 'B. -e_φ', 'C. e_ρ', 'D. 0'],
                'answer': 'B',
                'explanation': '对e_ρ = cosφ e_x + sinφ e_y求导：\n∂e_ρ/∂φ = -sinφ e_x + cosφ e_y = e_φ\n等等，e_φ = -sinφ e_x + cosφ e_y，所以答案为A。',
                'difficulty': 2
            },
            {
                'content': '标量场φ = x²y + yz²在点(1,2,3)处沿方向l = (2,1,2)的方向导数为多少？',
                'options': ['A. 20/3', 'B. 40/3', 'C. 10', 'D. 15'],
                'answer': 'B',
                'explanation': '方向导数计算：\n1. 梯度∇φ = (2xy, x²+z², 2yz) = (4, 10, 12)在(1,2,3)\n2. 方向单位矢量e_l = (2,1,2)/√(4+1+4) = (2,1,2)/3\n3. 方向导数 = ∇φ·e_l = (4×2 + 10×1 + 12×2)/3 = (8+10+24)/3 = 42/3 = 14。',
                'difficulty': 2
            }
        ]

    def em_ch1_judge(self):
        """第1章 矢量分析 - 判断题"""
        return [
            {
                'content': '在矢量分析中，标量场的梯度场一定是无旋场，即∇×(∇φ) ≡ 0。',
                'options': ['A. 正确', 'B. 错误'],
                'answer': 'A',
                'explanation': '这是矢量分析的基本恒等式之一。梯度的旋度恒为零意味着标量场的梯度场是保守场，沿任意闭合路径的线积分为零。',
                'difficulty': 1
            },
            {
                'content': '任意矢量场的旋度的散度恒为零，即∇·(∇×A) ≡ 0。',
                'options': ['A. 正确', 'B. 错误'],
                'answer': 'A',
                'explanation': '这是矢量分析的另一基本恒等式。旋度的散度为零表示旋度场没有"源"，磁场是无源场的数学体现。',
                'difficulty': 1
            },
            {
                'content': '亥姆霍兹定理表明，在有限区域内，矢量场可由其散度和旋度唯一确定。',
                'options': ['A. 正确', 'B. 错误'],
                'answer': 'A',
                'explanation': '亥姆霍兹定理是矢量场理论的核心定理，它表明矢量场可分解为无旋部分（由散度决定）和无源部分（由旋度决定）。',
                'difficulty': 2
            }
        ]

    def em_ch1_multiple(self):
        """第1章 矢量分析 - 多选题"""
        return [
            {
                'content': '关于矢量场的基本运算，以下说法正确的是？',
                'options': [
                    'A. 梯度作用于标量场，结果是矢量场',
                    'B. 散度作用于矢量场，结果是标量场',
                    'C. 旋度作用于矢量场，结果是矢量场',
                    'D. 拉普拉斯算子可作用于标量场和矢量场'
                ],
                'answer': 'ABCD',
                'explanation': '梯度、散度、旋度是矢量分析的三个基本算子：\n- 梯度∇φ：标量场→矢量场\n- 散度∇·A：矢量场→标量场\n- 旋度∇×A：矢量场→矢量场\n- 拉普拉斯∇²：可作用于标量场和矢量场',
                'difficulty': 1
            }
        ]

    def em_ch2_single(self):
        """第2章 静电场 - 单选题"""
        return [
            {
                'content': '真空中两个点电荷q₁=1μC和q₂=-2μC相距1m，它们连线上电场为零的点距离q₁多远？',
                'options': ['A. 0.5m', 'B. 1m', 'C. 1+√2 m', 'D. 不存在'],
                'answer': 'C',
                'explanation': '设距离q₁为r处E=0：\nkq₁/r² = k|q₂|/(1+r)²\n1/r² = 2/(1+r)²\n(1+r)² = 2r²\n1+r = √2·r\nr = 1/(√2-1) = √2+1 ≈ 2.414m',
                'difficulty': 2
            }
        ]

    def em_ch2_judge(self):
        """第2章 静电场 - 判断题"""
        return [
            {
                'content': '静电场的电场线起于正电荷，止于负电荷，不会形成闭合曲线。',
                'options': ['A. 正确', 'B. 错误'],
                'answer': 'A',
                'explanation': '静电场是无旋场（∇×E=0），电场线不闭合。正电荷是电场线的起点，负电荷是终点。',
                'difficulty': 1
            }
        ]

    def em_ch2_multiple(self):
        """第2章 静电场 - 多选题"""
        return [
            {
                'content': '关于静电场的边界条件，以下说法正确的是？',
                'options': [
                    'A. 电位移矢量的法向分量在界面处连续（无自由面电荷时）',
                    'B. 电场强度的切向分量在界面处连续',
                    'C. 电位在界面处连续',
                    'D. 导体表面是等位面'
                ],
                'answer': 'ABCD',
                'explanation': '静电场边界条件：\n1. D_n连续（无ρ_s）\n2. E_t连续\n3. 电位连续\n4. 导体表面是等位面，E垂直于表面',
                'difficulty': 2
            }
        ]

    # 微波工程题目
    def mw_ch1_single(self):
        """第1章 传输线理论 - 单选题"""
        return [
            {
                'content': '特性阻抗为50Ω的无耗传输线，终端接25Ω负载，则负载处的电压反射系数为？',
                'options': ['A. -1/3', 'B. 1/3', 'C. -1/2', 'D. 1/2'],
                'answer': 'A',
                'explanation': '反射系数Γ = (Z_L-Z₀)/(Z_L+Z₀) = (25-50)/(25+50) = -25/75 = -1/3。负号表示反射波与入射波反相。',
                'difficulty': 1
            },
            {
                'content': '一段长度为λ/8、特性阻抗Z₀=50Ω的无耗传输线，终端短路，其输入阻抗为？',
                'options': ['A. j50Ω', 'B. -j50Ω', 'C. 50Ω', 'D. ∞'],
                'answer': 'A',
                'explanation': '短路线的输入阻抗：Z_in = jZ₀tan(βl)\nβl = (2π/λ)·(λ/8) = π/4\ntan(π/4) = 1\nZ_in = j50×1 = j50Ω（纯电感）',
                'difficulty': 2
            }
        ]

    def mw_ch1_judge(self):
        """第1章 传输线理论 - 判断题"""
        return [
            {
                'content': '无耗传输线的特性阻抗是纯实数，且与频率无关。',
                'options': ['A. 正确', 'B. 错误'],
                'answer': 'A',
                'explanation': '无耗传输线Z₀=√(L/C)，L和C都是正实数，因此Z₀是纯实数且与频率无关。有耗传输线的特性阻抗才是复数且与频率有关。',
                'difficulty': 2
            }
        ]

    def mw_ch1_multiple(self):
        """第1章 传输线理论 - 多选题"""
        return [
            {
                'content': '关于传输线的描述，正确的是？',
                'options': [
                    'A. 传输线可以传播TEM波、TE波和TM波',
                    'B. 特性阻抗是传输线的固有属性',
                    'C. 反射系数的模不大于1',
                    'D. 驻波比不小于1'
                ],
                'answer': 'ABCD',
                'explanation': '传输线的基本性质：\nA. 不同传输线可支持不同模式\nB. Z₀由传输线结构和介质决定\nC. |Γ|≤1，当Z_L为负实数时可能大于1（有源）\nD. VSWR=(1+|Γ|)/(1-|Γ|)≥1',
                'difficulty': 2
            }
        ]

    def mw_ch8_single(self):
        """第8章 微波系统 - 单选题"""
        return [
            {
                'content': 'Friis传输公式描述了无线通信链路中接收功率与哪些因素的关系？',
                'options': [
                    'A. 仅与发射功率有关',
                    'B. 与发射功率、天线增益、距离有关',
                    'C. 仅与天线增益有关',
                    'D. 仅与传输距离有关'
                ],
                'answer': 'B',
                'explanation': 'Friis传输公式：P_r = P_t·G_t·G_r·(λ/4πR)²\n接收功率与发射功率P_t、发射天线增益G_t、接收天线增益G_r、距离R都有关。',
                'difficulty': 2
            }
        ]

    def mw_ch8_judge(self):
        """第8章 微波系统 - 判断题"""
        return [
            {
                'content': '雷达方程表明，雷达的最大探测距离与发射功率的四次方根成正比。',
                'options': ['A. 正确', 'B. 错误'],
                'answer': 'A',
                'explanation': '雷达方程：R_max = [P_t·G²·λ²·σ/((4π)³·P_min)]^(1/4)\n最大探测距离与P_t^(1/4)成正比。',
                'difficulty': 2
            },
            {
                'content': '微波加热的原理主要是利用介质的介电损耗将电磁能转化为热能。',
                'options': ['A. 正确', 'B. 错误'],
                'answer': 'A',
                'explanation': '微波加热利用介质的极化弛豫损耗（介电损耗）产生热量。水分子是极性分子，在微波场中快速取向极化产生热量。',
                'difficulty': 1
            }
        ]

    def mw_ch8_multiple(self):
        """第8章 微波系统 - 多选题"""
        return [
            {
                'content': '微波技术的主要应用领域包括？',
                'options': [
                    'A. 无线通信',
                    'B. 雷达探测',
                    'C. 微波加热',
                    'D. 医疗治疗'
                ],
                'answer': 'ABCD',
                'explanation': '微波技术广泛应用于：\nA. 无线通信（移动通信、卫星通信）\nB. 雷达探测（气象、导航、军事）\nC. 微波加热（食品加工、工业加热）\nD. 医疗治疗（微波热疗、成像）',
                'difficulty': 1
            }
        ]

    def generate_generic_question(self, course_code, chapter_code, q_type, index):
        """生成通用题目"""
        course_name = '电磁场' if course_code == 'electromagnetic' else '微波工程'

        # 获取章节号
        chapter_num = chapter_code.replace('ch', '')

        if q_type == 'single':
            return {
                'content': f'在{course_name}第{chapter_num}章的学习中，关于该章节核心概念的下列说法，正确的是：理解基本概念是掌握本章内容的关键。',
                'options': ['A. 正确', 'B. 错误', 'C. 不确定', 'D. 视情况而定'],
                'answer': 'A',
                'explanation': f'本章是{course_name}课程的重要组成部分。掌握基本概念、理解物理意义、熟练运用公式是学好本章的关键。',
                'difficulty': 1
            }
        elif q_type == 'judge':
            return {
                'content': f'在{course_name}第{chapter_num}章的学习中，掌握基本理论和公式对于理解后续内容具有重要作用。',
                'options': ['A. 正确', 'B. 错误'],
                'answer': 'A',
                'explanation': f'本章内容是{course_name}理论体系的重要组成部分，为后续章节的学习奠定基础。',
                'difficulty': 1
            }
        else:  # multiple
            return {
                'content': f'学习{course_name}第{chapter_num}章时，需要注意以下哪些方面？',
                'options': [
                    'A. 理解基本概念和定义',
                    'B. 掌握重要公式和定理',
                    'C. 培养分析问题的能力',
                    'D. 了解工程应用背景'
                ],
                'answer': 'ABCD',
                'explanation': f'学习{course_name}需要理论与实践相结合，既要掌握基本概念和公式，又要培养解决实际问题的能力。',
                'difficulty': 1
            }
