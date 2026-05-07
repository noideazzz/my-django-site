#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
生成完整正式习题的管理命令
针对测试占位符和简短题目，生成具有完整内容的正式习题
"""
from django.core.management.base import BaseCommand
from blog.models import Question, Course, Chapter
import re


class Command(BaseCommand):
    help = '将测试占位符和简短题目转化为完整正式习题'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='只显示将要修改的内容，不实际执行',
        )
        parser.add_argument(
            '--course',
            type=str,
            help='指定课程代码 (electromagnetic/microwave)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        course_code = options.get('course')

        self.stdout.write("=" * 80)
        self.stdout.write(self.style.MIGRATE_HEADING("正式习题生成工具"))
        self.stdout.write("=" * 80)

        if dry_run:
            self.stdout.write(self.style.WARNING("\n[模拟模式] 不会实际修改数据\n"))

        # 构建查询条件
        queryset = Question.objects.all()
        if course_code:
            queryset = queryset.filter(course__code=course_code)

        # 统计需要处理的题目
        placeholder_count = 0
        short_count = 0
        total_processed = 0

        for q in queryset:
            content = q.content.strip()
            # 检测占位符题目
            if self.is_placeholder(content):
                placeholder_count += 1
                if self.process_placeholder_question(q, dry_run):
                    total_processed += 1
            # 检测简短题目（但非占位符）
            elif len(content) < 25:
                short_count += 1
                if self.process_short_question(q, dry_run):
                    total_processed += 1

        self.stdout.write(f"\n发现 {placeholder_count} 道占位符题目")
        self.stdout.write(f"发现 {short_count} 道简短题目")
        self.stdout.write(f"共处理 {total_processed} 道题目")

        self.stdout.write("\n" + "=" * 80)
        if dry_run:
            self.stdout.write(f"[模拟完成]")
        else:
            self.stdout.write(self.style.SUCCESS("处理完成！"))
        self.stdout.write("=" * 80)

    def is_placeholder(self, content):
        """检测是否为占位符题目"""
        patterns = [
            r'第[\d一二三四五六七八]+章.*(?:判断|单选|多选)',
            r'第[\d]+章.*(?:判断|单选|多选)',
            r'^[\d一二三四五六七八]+章',
        ]
        for pattern in patterns:
            if re.search(pattern, content):
                return True
        return False

    def process_placeholder_question(self, question, dry_run):
        """处理占位符题目"""
        course_code = question.course.code
        chapter_code = question.chapter.code
        q_type = question.question_type
        q_id = question.id

        # 根据章节和题型获取新题目
        new_data = self.get_formal_question(course_code, chapter_code, q_type, q_id)

        if not new_data:
            return False

        if not dry_run:
            question.content = new_data['content']
            question.options = new_data['options']
            question.correct_answer = new_data['answer']
            question.explanation = new_data['explanation']
            if new_data.get('difficulty'):
                question.difficulty = new_data['difficulty']
            question.save()

        return True

    def process_short_question(self, question, dry_run):
        """处理简短题目 - 扩展内容"""
        course_code = question.course.code
        chapter_code = question.chapter.code
        content = question.content.strip()

        # 获取简短题目的扩展版本
        enhanced = self.enhance_short_content(course_code, chapter_code, content)

        if not enhanced:
            return False

        if not dry_run:
            if enhanced.get('content'):
                question.content = enhanced['content']
            if enhanced.get('explanation'):
                question.explanation = enhanced['explanation']
            question.save()

        return True

    def get_formal_question(self, course_code, chapter_code, q_type, q_id):
        """获取完整的正式习题"""
        if course_code == 'electromagnetic':
            return self.get_em_formal_question(chapter_code, q_type, q_id)
        elif course_code == 'microwave':
            return self.get_mw_formal_question(chapter_code, q_type, q_id)
        return None

    def get_em_formal_question(self, chapter_code, q_type, q_id):
        """获取电磁场课程正式习题"""

        # 第1章 矢量分析
        if chapter_code == 'ch1':
            questions = {
                'single': [
                    {
                        'content': '在圆柱坐标系中，标量场f(ρ,φ,z) = ρ²cosφ的梯度在点(1, 0, 0)处的值为多少？',
                        'options': ['A. 2e_ρ', 'B. 2e_ρ + e_φ', 'C. 2e_ρ - e_φ', 'D. e_ρ + 2e_φ'],
                        'answer': 'A',
                        'explanation': '圆柱坐标系中梯度公式：∇f = ∂f/∂ρ·e_ρ + (1/ρ)·∂f/∂φ·e_φ + ∂f/∂z·e_z\n计算：∂f/∂ρ = 2ρcosφ，在(1,0,0)处为2\n(1/ρ)·∂f/∂φ = -ρsinφ，在(1,0,0)处为0\n∂f/∂z = 0\n因此∇f = 2e_ρ',
                        'difficulty': 2
                    },
                    {
                        'content': '矢量场A = xe_x + ye_y + ze_z通过闭合曲面S（半径为R的球面）的通量为多少？',
                        'options': ['A. 0', 'B. 4πR²', 'C. 4πR³', 'D. 4πR³/3'],
                        'answer': 'C',
                        'explanation': '使用高斯散度定理：∮A·dS = ∫∫∫(∇·A)dV\n计算散度：∇·A = ∂(x)/∂x + ∂(y)/∂y + ∂(z)/∂z = 1 + 1 + 1 = 3\n体积分：∫∫∫3dV = 3×(4πR³/3) = 4πR³',
                        'difficulty': 2
                    },
                    {
                        'content': '关于矢量场旋度的物理意义，下列说法正确的是？',
                        'options': [
                            'A. 旋度表示矢量场在某点的发散程度',
                            'B. 旋度表示矢量场在某点的旋转强弱和转轴方向',
                            'C. 旋度表示矢量场在某点的最大变化率',
                            'D. 旋度表示矢量场在某点的源强度'
                        ],
                        'answer': 'B',
                        'explanation': '旋度(Curl)的物理意义：\n1. 大小：表示矢量场在该点的旋转程度（涡旋强度）\n2. 方向：表示旋转的转轴方向（按右手定则）\n3. ∇×A = 0表示无旋场（保守场）\n4. 对比：散度表示发散程度，梯度表示变化率',
                        'difficulty': 1
                    }
                ],
                'judge': [
                    {
                        'content': '在正交曲线坐标系中，拉梅系数h_i满足h_i = |∂r/∂u_i|，其中u_i为广义坐标。',
                        'options': ['A. 正确', 'B. 错误'],
                        'answer': 'A',
                        'explanation': '拉梅系数（Lamé系数）的定义：\nh_i = |∂r/∂u_i| = √[(∂x/∂u_i)² + (∂y/∂u_i)² + (∂z/∂u_i)²]\n它表示坐标u_i变化时，位置矢量的变化率，是度量系数的一部分。',
                        'difficulty': 2
                    },
                    {
                        'content': '亥姆霍兹定理指出：在有限区域内，一个矢量场可唯一地分解为一个无旋部分和一个无源部分之和。',
                        'options': ['A. 正确', 'B. 错误'],
                        'answer': 'A',
                        'explanation': '亥姆霍兹定理（Helmholtz定理）是矢量场理论的重要定理：\n任意矢量场F可分解为：F = -∇φ + ∇×A\n其中-∇φ是无旋部分（∇×(-∇φ) = 0），∇×A是无源部分（∇·(∇×A) = 0）。\n该定理是电磁场分析中引入标量势和矢量势的理论基础。',
                        'difficulty': 2
                    }
                ],
                'multiple': [
                    {
                        'content': '关于矢量分析中的重要恒等式，以下哪些是正确的？',
                        'options': [
                            'A. ∇×(∇φ) = 0（梯度的旋度恒为零）',
                            'B. ∇·(∇×A) = 0（旋度的散度恒为零）',
                            'C. ∇·(∇φ) = ∇²φ（梯度的散度等于拉普拉斯）',
                            'D. ∇×(∇×A) = ∇(∇·A) - ∇²A（矢量旋度的旋度）'
                        ],
                        'answer': 'ABCD',
                        'explanation': '矢量分析中的四大恒等式：\n1. ∇×(∇φ) ≡ 0：梯度的旋度恒为零，任何标量场的梯度场都是无旋场\n2. ∇·(∇×A) ≡ 0：旋度的散度恒为零，任何矢量场的旋度场都是无源场\n3. ∇·(∇φ) = ∇²φ：梯度的散度等于拉普拉斯算子作用，即标量场的二阶导数之和\n4. ∇×(∇×A) = ∇(∇·A) - ∇²A：矢量旋度的旋度分解为梯度散度与拉普拉斯之差',
                        'difficulty': 3
                    }
                ]
            }
            return self.select_question(questions, q_type, q_id)

        # 第2章 静电场
        elif chapter_code == 'ch2':
            questions = {
                'single': [
                    {
                        'content': '在均匀电场E₀中放入一个导体球，达到静电平衡后，导体球表面的感应电荷分布如何？',
                        'options': [
                            'A. 均匀分布',
                            'B. 沿电场方向分布较多',
                            'C. 垂直于电场方向分布较多',
                            'D. 只在球的两极分布'
                        ],
                        'answer': 'B',
                        'explanation': '导体球在均匀外电场中的静电感应：\n1. 导体内部电场为零\n2. 感应电荷在表面分布\n3. 沿外电场方向（电场来向）感应负电荷，另一侧感应正电荷\n4. 电荷密度与表面切向电场有关，在θ=0和θ=π处最大\n5. 形成电偶极子分布',
                        'difficulty': 2
                    },
                    {
                        'content': '真空中半径为R的均匀带电球面（电荷量为Q）在球心处产生的电位为多少？',
                        'options': ['A. Q/(4πε₀R)', 'B. Q/(4πε₀R²)', 'C. 0', 'D. ∞'],
                        'answer': 'A',
                        'explanation': '均匀带电球面的电位计算：\n1. 球面电荷产生的电场：\n   - r > R时，E = Q/(4πε₀r²)（球外等效于点电荷）\n   - r < R时，E = 0（高斯定理）\n2. 球心电位：φ = ∫[∞→0]E·dr\n   = ∫[∞→R]Q/(4πε₀r²)dr + ∫[R→0]0dr\n   = Q/(4πε₀R)\n3. 球面是等位面',
                        'difficulty': 2
                    }
                ],
                'judge': [
                    {
                        'content': '静电场的等位面与电场线处处正交。',
                        'options': ['A. 正确', 'B. 错误'],
                        'answer': 'A',
                        'explanation': '等位面与电场线的关系：\n1. 等位面上各点电位相等\n2. 沿等位面移动电荷，电场力不做功：E·dl = 0\n3. 这意味着E垂直于等位面内的任意位移dl\n4. 因此电场线（沿E方向）与等位面处处正交\n5. 这是静电场的重要几何性质',
                        'difficulty': 1
                    },
                    {
                        'content': '在静电场中，导体表面的电场强度只有法向分量，切向分量为零。',
                        'options': ['A. 正确', 'B. 错误'],
                        'answer': 'A',
                        'explanation': '导体表面的电场边界条件：\n1. 导体内部电场为零（静电平衡）\n2. 电场切向分量连续：E_{1t} = E_{2t}\n3. 导体内部E_{2t} = 0，所以外部E_{1t} = 0\n4. 电场只有法向分量，且E_n = σ/ε₀\n5. 导体表面是等位面',
                        'difficulty': 2
                    }
                ],
                'multiple': [
                    {
                        'content': '关于静电场中导体的性质，以下哪些说法是正确的？',
                        'options': [
                            'A. 导体内部电场强度处处为零',
                            'B. 导体是等位体，表面是等位面',
                            'C. 导体表面电场垂直于表面',
                            'D. 导体内部电荷密度处处为零'
                        ],
                        'answer': 'ABCD',
                        'explanation': '静电场中导体的基本性质：\n1. 导体内部E=0：自由电荷移动直到抵消外电场\n2. 导体是等位体：∵E=-∇φ=0，∴φ=常数\n3. 表面电场垂直：切向分量必须连续，内部E_t=0，∴外部E_t=0\n4. 内部无电荷：由高斯定理∇·E=ρ/ε₀，E=0⇒ρ=0\n5. 所有电荷分布在导体表面',
                        'difficulty': 2
                    }
                ]
            }
            return self.select_question(questions, q_type, q_id)

        # 其他章节省略...使用简短题目增强
        return None

    def get_mw_formal_question(self, chapter_code, q_type, q_id):
        """获取微波工程课程正式习题"""

        # 第1章 传输线理论
        if chapter_code == 'ch1':
            questions = {
                'single': [
                    {
                        'content': '一段长度为λ/4、特性阻抗为Z₀的无耗传输线，终端接负载Z_L。其输入阻抗Z_in与Z_L的关系是？',
                        'options': [
                            'A. Z_in = Z_L',
                            'B. Z_in = Z₀²/Z_L',
                            'C. Z_in = Z₀·Z_L',
                            'D. Z_in = Z₀ + Z_L'
                        ],
                        'answer': 'B',
                        'explanation': 'λ/4传输线的阻抗变换特性：\n1. 输入阻抗公式：Z_in = Z₀·(Z_L + jZ₀tanβl)/(Z₀ + jZ_Ltanβl)\n2. 当l = λ/4时，βl = (2π/λ)·(λ/4) = π/2\n3. tan(π/2) → ∞，公式化简为Z_in = Z₀²/Z_L\n4. 应用：λ/4阻抗变换器\n   - 用于阻抗匹配\n   - 选择Z₀ = √(Z_in·Z_L)',
                        'difficulty': 2
                    },
                    {
                        'content': '无耗传输线的特性阻抗Z₀=50Ω，终端接Z_L=100Ω的负载。传输线上的驻波比VSWR为多少？',
                        'options': ['A. 1', 'B. 2', 'C. 0.5', 'D. 4'],
                        'answer': 'B',
                        'explanation': '驻波比计算：\n1. 反射系数：Γ = (Z_L - Z₀)/(Z_L + Z₀) = (100-50)/(100+50) = 50/150 = 1/3\n2. 驻波比：VSWR = (1+|Γ|)/(1-|Γ|)\n3. 代入：VSWR = (1+1/3)/(1-1/3) = (4/3)/(2/3) = 2\n4. 物理意义：\n   - VSWR=1表示完全匹配\n   - VSWR=2表示有反射，最大电压是最小电压的2倍',
                        'difficulty': 2
                    },
                    {
                        'content': '在传输线上，电压波腹处的输入阻抗具有什么特性？',
                        'options': [
                            'A. 纯电阻性且最大',
                            'B. 纯电阻性且最小',
                            'C. 纯电抗性',
                            'D. 为零'
                        ],
                        'answer': 'A',
                        'explanation': '传输线电压波腹处的阻抗特性：\n1. 电压波腹位置：反射波与入射波同相叠加处\n2. 此时电流波谷（最小）\n3. 阻抗Z = V/I，V最大、I最小，所以Z最大\n4. 在波腹处，反射系数为实数且为正，阻抗为纯电阻性\n5. Z_max = Z₀·VSWR（最大值）\n6. 波节处Z_min = Z₀/VSWR（最小值，纯电阻）',
                        'difficulty': 2
                    }
                ],
                'judge': [
                    {
                        'content': '在无耗传输线上，任意位置的输入阻抗与负载阻抗之间的关系可以通过史密斯圆图直观地表示和分析。',
                        'options': ['A. 正确', 'B. 错误'],
                        'answer': 'A',
                        'explanation': '史密斯圆图在传输线分析中的应用：\n1. 圆图将反射系数、归一化阻抗、驻波比等参数映射到复平面\n2. 沿传输线移动对应于在圆图上沿等反射系数圆旋转\n3. 向信号源移动：顺时针旋转\n4. 向负载移动：逆时针旋转\n5. 旋转一周（360°）对应线长变化λ/2\n6. 圆图是微波工程中分析传输线问题的重要图形工具',
                        'difficulty': 1
                    },
                    {
                        'content': '当传输线终端短路时，距离终端λ/4处的输入阻抗为无穷大（开路）。',
                        'options': ['A. 正确', 'B. 错误'],
                        'answer': 'A',
                        'explanation': 'λ/4传输线的阻抗变换特性验证：\n1. 短路时Z_L = 0\n2. 输入阻抗公式：Z_in = jZ₀tan(βl)\n3. 当l = λ/4时，βl = π/2\n4. tan(π/2) → ∞\n5. 因此Z_in → ∞（开路）\n6. 反之，终端开路时，λ/4处等效短路\n7. 应用：λ/4短路/开路支节用于阻抗匹配',
                        'difficulty': 2
                    }
                ],
                'multiple': [
                    {
                        'content': '关于传输线的反射系数，以下哪些说法是正确的？',
                        'options': [
                            'A. 反射系数Γ = (Z_L - Z₀)/(Z_L + Z₀)',
                            'B. 匹配时Γ = 0',
                            'C. 全反射时|Γ| = 1',
                            'D. 反射系数的相位随传输线位置而变化'
                        ],
                        'answer': 'ABCD',
                        'explanation': '反射系数的性质：\n1. 定义：Γ = (Z_L - Z₀)/(Z_L + Z₀)，在负载处定义\n2. 匹配时Z_L = Z₀，Γ = 0，无反射\n3. 全反射情况：\n   - 开路：Z_L→∞，Γ=1\n   - 短路：Z_L=0，Γ=-1\n   - 纯电抗：|Z_L|→∞，|Γ|=1\n4. 沿线变化：Γ(l) = Γ_L·e^(-j2βl)，相位随位置变化\n5. |Γ|沿线不变（无耗线）',
                        'difficulty': 2
                    }
                ]
            }
            return self.select_question(questions, q_type, q_id)

        # 其他章节...简化为使用通用增强
        return None

    def select_question(self, questions_dict, q_type, q_id):
        """根据题型和ID选择合适的题目"""
        if q_type not in questions_dict:
            return None

        type_questions = questions_dict[q_type]
        if not type_questions:
            return None

        # 使用ID来选择题目，确保同类型题目有不同的内容
        index = q_id % len(type_questions)
        return type_questions[index]

    def enhance_short_content(self, course_code, chapter_code, original_content):
        """增强简短题目的内容"""
        # 构建增强内容库
        enhancements = {
            # 电磁场 - 第1章 矢量分析
            ('electromagnetic', 'ch1'): {
                '标量场的梯度场一定是无旋场': {
                    'content': '在矢量分析中，关于标量场梯度的性质，以下说法是否正确：标量场的梯度场一定是无旋场。',
                    'explanation': '标量场的梯度∇φ具有以下重要性质：\n1. 梯度是一个矢量场，指向标量场增长最快的方向\n2. 梯度的旋度恒为零：∇×(∇φ) = 0\n3. 因此，任何标量场的梯度场都是无旋场（保守场），这是矢量分析中的基本定理之一。\n本题答案为正确。'
                }
            },
            # 电磁场 - 第3章 恒定电流场
            ('electromagnetic', 'ch3'): {
                '电流密度是标量': {
                    'content': '在恒定电流场理论中，关于电流密度的性质，以下说法是否正确：电流密度是一个标量。',
                    'explanation': '电流密度J是一个矢量，其定义和性质如下：\n1. 大小：单位时间内通过单位垂直面积的电荷量\n2. 方向：正电荷定向移动的方向\n3. 与电流的关系：I = ∫∫ J·dS\n4. 微分形式的欧姆定律：J = σE\n因此电流密度是矢量而非标量，本题答案为错误。'
                }
            },
            # 微波工程 - 第1章 传输线理论
            ('microwave', 'ch1'): {
                '无耗传输线的相速度等于光速': {
                    'content': '关于无耗传输线中电磁波相速度的下列说法是否正确：无耗传输线中的相速度总是等于真空中的光速。',
                    'explanation': '传输线中相速度的分析：\n1. 相速度定义：v_p = ω/β\n2. 无耗传输线：β = ω√(LC)，v_p = 1/√(LC)\n3. 与光速的关系：\n   - 对于平行双线和同轴线：v_p = c/√ε_r\n   - 只有当ε_r = 1（空气线）时，v_p = c\n   - 一般介质填充时，v_p < c\n4. 结论：相速度取决于传输线填充介质的介电常数\n本题答案为错误。'
                },
                '匹配时驻波比为1': {
                    'content': '关于传输线匹配状态下的驻波比特性，以下说法是否正确：传输线匹配时，驻波比（VSWR）等于1。',
                    'explanation': '传输线匹配与驻波比的关系：\n1. 匹配定义：负载阻抗Z_L等于特性阻抗Z_0\n2. 反射系数：Γ = (Z_L - Z_0)/(Z_L + Z_0)，匹配时Γ = 0\n3. 驻波比定义：VSWR = (1+|Γ|)/(1-|Γ|)\n4. 匹配时：VSWR = (1+0)/(1-0) = 1\n5. 物理意义：VSWR=1表示无反射波，只有行波\n本题答案为正确。'
                }
            }
        }

        key = (course_code, chapter_code)
        if key in enhancements:
            chapter_enhancements = enhancements[key]
            for pattern, data in chapter_enhancements.items():
                if pattern in original_content or original_content in pattern:
                    return data

        return None
