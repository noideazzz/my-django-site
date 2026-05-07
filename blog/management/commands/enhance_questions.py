#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
将测试题转化为完整正式习题的管理命令
- 扩展简短题目内容
- 补充必要的背景信息
- 完善答案解析
"""
from django.core.management.base import BaseCommand
from blog.models import Question, Course, Chapter
import json


class Command(BaseCommand):
    help = '将测试题转化为完整正式习题'

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
        parser.add_argument(
            '--chapter',
            type=str,
            help='指定章节代码 (如 ch1, ch2)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        course_code = options.get('course')
        chapter_code = options.get('chapter')

        self.stdout.write("=" * 80)
        self.stdout.write(self.style.MIGRATE_HEADING("测试题转化工具"))
        self.stdout.write("=" * 80)

        if dry_run:
            self.stdout.write(self.style.WARNING("\n[模拟模式] 不会实际修改数据\n"))

        # 构建查询条件
        queryset = Question.objects.all()
        if course_code:
            queryset = queryset.filter(course__code=course_code)
        if chapter_code:
            queryset = queryset.filter(chapter__code=chapter_code)

        # 筛选简短题目（内容长度<20字符或解析为空）
        short_questions = []
        for q in queryset:
            content_len = len(q.content.strip())
            explanation_len = len(q.explanation.strip()) if q.explanation else 0
            # 判断是否为测试题：内容过短或解析过于简单
            if content_len < 20 or explanation_len < 15:
                short_questions.append(q)

        total = len(short_questions)
        self.stdout.write(f"\n发现 {total} 道需要转化的测试题\n")

        if total == 0:
            self.stdout.write(self.style.SUCCESS("没有需要转化的题目"))
            return

        # 统计信息
        stats = {}
        for q in short_questions:
            key = f"{q.course.name}-{q.chapter.name}"
            if key not in stats:
                stats[key] = 0
            stats[key] += 1

        self.stdout.write("\n各章节分布：")
        for key, count in sorted(stats.items()):
            self.stdout.write(f"  {key}: {count}题")

        # 开始转化
        enhanced_count = 0
        for q in short_questions:
            enhanced = self.enhance_question(q, dry_run)
            if enhanced:
                enhanced_count += 1

        self.stdout.write("\n" + "=" * 80)
        if dry_run:
            self.stdout.write(f"[模拟完成] 共可转化 {enhanced_count} 道题目")
        else:
            self.stdout.write(self.style.SUCCESS(f"转化完成！共处理 {enhanced_count} 道题目"))
        self.stdout.write("=" * 80)

    def enhance_question(self, question, dry_run):
        """转化单个题目"""
        course_code = question.course.code
        chapter_code = question.chapter.code
        q_type = question.question_type
        original_content = question.content.strip()

        # 根据章节获取增强内容
        enhanced_data = self.get_enhanced_content(
            course_code, chapter_code, q_type,
            original_content, question.options, question.correct_answer
        )

        if not enhanced_data:
            return False

        if not dry_run:
            # 更新题目
            if enhanced_data.get('content'):
                question.content = enhanced_data['content']
            if enhanced_data.get('options'):
                question.options = enhanced_data['options']
            if enhanced_data.get('explanation'):
                question.explanation = enhanced_data['explanation']
            question.save()

        return True

    def get_enhanced_content(self, course_code, chapter_code, q_type,
                             original_content, options, answer):
        """根据章节和题型获取增强后的内容"""

        # 电磁场与电磁波课程
        if course_code == 'electromagnetic':
            return self.get_em_content(chapter_code, q_type, original_content,
                                        options, answer)
        # 微波工程课程
        elif course_code == 'microwave':
            return self.get_mw_content(chapter_code, q_type, original_content,
                                        options, answer)
        return None

    def get_em_content(self, chapter_code, q_type, original, options, answer):
        """获取电磁场与电磁波课程的增强内容"""

        # 第1章 矢量分析
        if chapter_code == 'ch1':
            enhancements = {
                '标量场的梯度场一定是无旋场': {
                    'content': '在矢量分析中，关于标量场梯度的性质，以下说法是否正确：标量场的梯度场一定是无旋场。',
                    'explanation': '标量场的梯度∇φ具有以下重要性质：\n1. 梯度是一个矢量场，指向标量场增长最快的方向\n2. 梯度的旋度恒为零：∇×(∇φ) = 0\n3. 因此，任何标量场的梯度场都是无旋场（保守场），这是矢量分析中的基本定理之一。\n本题答案为正确。'
                },
                '矢量场的旋度场一定是无源场': {
                    'content': '在矢量分析中，考虑矢量场旋度的散度性质：矢量场的旋度场是否一定是无源场（散度为零）？',
                    'explanation': '根据矢量分析的基本恒等式，任意矢量场A的旋度的散度恒为零：∇·(∇×A) = 0\n这表明：\n1. 旋度场本身是无源场\n2. 旋度描述的是场的旋转特性，不涉及场的"源"\n3. 这是麦克斯韦方程组中磁场无源性的数学基础\n本题答案为正确。'
                },
                '下列恒等式正确的是': {
                    'content': '在矢量分析中，以下关于场论恒等式的描述，哪些是正确的？（多选）\nA. 梯度的旋度恒为零：∇×(∇φ) = 0\nB. 旋度的散度恒为零：∇·(∇×A) = 0\nC. 任意矢量场都可分解为无旋部分和无源部分\nD. 散度描述场的旋转特性',
                    'options': ['A. 梯度的旋度恒为零', 'B. 旋度的散度恒为零', 'C. 亥姆霍兹分解定理', 'D. 散度描述旋转特性'],
                    'explanation': '矢量分析中的重要恒等式包括：\n1. ∇×(∇φ) ≡ 0：梯度的旋度恒为零（保守场性质）\n2. ∇·(∇×A) ≡ 0：旋度的散度恒为零\n3. 亥姆霍兹分解定理：任意矢量场可分解为无旋部分和无源部分\n4. 散度描述场的"源"特性，旋度描述场的旋转特性\n因此正确答案是A、B、C。'
                }
            }
            return self.match_enhancement(original, enhancements)

        # 第2章 静电场
        elif chapter_code == 'ch2':
            enhancements = {
                '电场线是闭合曲线': {
                    'content': '关于静电场中电场线的性质，以下说法是否正确：静电场中的电场线是闭合曲线。',
                    'explanation': '静电场的电场线具有以下性质：\n1. 起于正电荷（或无穷远），止于负电荷（或无穷远）\n2. 电场线不会形成闭合曲线（这是静电场无旋性的体现）\n3. 静电场的环路定理∮E·dl = 0表明电场线不闭合\n4. 只有时变电磁场中才可能出现闭合的电场线（涡旋电场）\n本题答案为错误。'
                }
            }
            return self.match_enhancement(original, enhancements)

        # 第3章 恒定电流场
        elif chapter_code == 'ch3':
            enhancements = {
                '电流密度是标量': {
                    'content': '在恒定电流场理论中，关于电流密度的性质，以下说法是否正确：电流密度是一个标量。',
                    'explanation': '电流密度J是一个矢量，其定义和性质如下：\n1. 大小：单位时间内通过单位垂直面积的电荷量\n2. 方向：正电荷定向移动的方向\n3. 与电流的关系：I = ∫∫ J·dS\n4. 微分形式的欧姆定律：J = σE\n因此电流密度是矢量而非标量，本题答案为错误。'
                },
                '电阻并联时': {
                    'content': '在直流电路分析中，关于电阻并联的特性，以下哪些说法是正确的？（多选）\nA. 总电阻的倒数等于各电阻倒数之和\nB. 各电阻两端电压相等\nC. 总电流等于各支路电流之和\nD. 功率分配与电阻成正比',
                    'options': ['A. 1/R总 = Σ(1/Ri)', 'B. 各电阻电压相等', 'C. 总电流等于各支路电流之和', 'D. 功率与电阻成正比'],
                    'explanation': '电阻并联电路的基本特性：\n1. 电压特性：各并联电阻两端电压相等\n2. 电流特性：总电流I = I₁ + I₂ + I₃ + ...\n3. 等效电阻：1/R = 1/R₁ + 1/R₂ + 1/R₃ + ...\n4. 功率分配：P = U²/R，功率与电阻成反比\n5. 分流公式：I₁/I₂ = R₂/R₁\n因此正确答案是A、B、C。'
                },
                '电阻串联时': {
                    'content': '在直流电路分析中，关于电阻串联的特性，以下哪些说法是正确的？（多选）\nA. 总电阻等于各电阻之和\nB. 各电阻通过的电流相等\nC. 总电压等于各电阻电压之和\nD. 功率分配与电阻成反比',
                    'options': ['A. R总 = ΣRi', 'B. 各电阻电流相等', 'C. 总电压等于各电阻电压之和', 'D. 功率与电阻成反比'],
                    'explanation': '电阻串联电路的基本特性：\n1. 电流特性：通过各串联电阻的电流相等\n2. 电压特性：总电压U = U₁ + U₂ + U₃ + ...\n3. 等效电阻：R = R₁ + R₂ + R₃ + ...\n4. 功率分配：P = I²R，功率与电阻成正比\n5. 分压公式：U₁/U₂ = R₁/R₂\n因此正确答案是A、B、C。'
                }
            }
            return self.match_enhancement(original, enhancements)

        # 第4章 恒定磁场
        elif chapter_code == 'ch4':
            enhancements = {
                '磁场线是闭合曲线': {
                    'content': '关于恒定磁场的磁感应线（B线）性质，以下说法是否正确：磁感应线是闭合曲线。',
                    'explanation': '磁感应线（磁场线）的基本性质：\n1. 磁感应线是无头无尾的闭合曲线\n2. 这是磁场高斯定理∇·B = 0的直接结果\n3. 磁场是无源场，不存在磁单极子\n4. 磁感应线要么形成闭合回路，要么从无穷远来向无穷远去\n5. 这与电场线（起于正电荷止于负电荷）形成鲜明对比\n本题答案为正确。'
                },
                '磁场是无源有旋场': {
                    'content': '根据麦克斯韦方程组对恒定磁场的描述，以下说法是否正确：恒定磁场是无源有旋场。',
                    'explanation': '恒定磁场的基本场特性：\n1. 无源性：∇·B = 0（磁场高斯定律）\n   - 不存在磁单极子\n   - 磁感应线是闭合曲线\n2. 有旋性：∇×H = J（安培环路定律）\n   - 磁场由电流激发\n   - 具有旋涡性质\n3. 因此恒定磁场是"有旋无源场"\n本题答案为正确。'
                },
                '磁单极子存在': {
                    'content': '关于磁单极子（磁荷）的存在性问题，以下说法是否正确：自然界中存在磁单极子。',
                    'explanation': '关于磁单极子的科学认知：\n1. 麦克斯韦方程组：∇·B = 0 明确表明磁场无源，不存在磁单极子\n2. 实验验证：迄今为止，所有寻找磁单极子的实验均未成功\n3. 理论预言：狄拉克从量子力学角度预言磁单极子可能存在，但未被实验证实\n4. 与电荷对比：电场有源（∇·D = ρ），存在正负电荷；磁场无源，无磁单极子\n5. 磁现象的本质是电流或变化的电场产生的\n本题答案为错误。'
                }
            }
            return self.match_enhancement(original, enhancements)

        # 第5章 时变电磁场
        elif chapter_code == 'ch5':
            enhancements = {
                '电磁波是横波': {
                    'content': '关于电磁波的传播特性，以下说法是否正确：电磁波是横波。',
                    'explanation': '电磁波的横波特性和传播特点：\n1. 横波定义：振动方向与传播方向垂直的波\n2. 电磁波中：电场E、磁场H都与传播方向k垂直\n3. 三者关系：E⊥H，E⊥k，H⊥k，且满足右手定则\n4. TEM波：横电磁波，E和H都在垂直于传播方向的平面内\n5. 这与纵波（如声波）形成对比\n6. 横波特性是电磁波能传播极化的原因\n本题答案为正确。'
                },
                '全电流包括': {
                    'content': '根据麦克斯韦提出的全电流概念，位移电流与传导电流共同构成全电流。以下哪些电流属于全电流的范畴？（多选）\nA. 传导电流\nB. 位移电流\nC. 运流电流\nD. 磁化电流',
                    'options': ['A. 传导电流', 'B. 位移电流', 'C. 运流电流', 'D. 磁化电流'],
                    'explanation': '全电流定律和电流的分类：\n1. 传导电流：自由电荷在导体中的定向运动（J = σE）\n2. 位移电流：电位移矢量的时间变化率（J_d = ∂D/∂t）\n3. 运流电流：带电物体运动形成的电流\n4. 全电流安培定律：∇×H = J + ∂D/∂t\n5. 磁化电流是等效电流，不属于全电流\n全电流体现了电流的连续性，在时变场中尤为重要。正确答案是A、B、C。'
                }
            }
            return self.match_enhancement(original, enhancements)

        # 第6章 平面电磁波
        elif chapter_code == 'ch6':
            enhancements = {
                '驻波中能量不传播': {
                    'content': '关于电磁波驻波的能量特性，以下说法是否正确：在驻波中，电磁能量不向外传播。',
                    'explanation': '驻波的能量特性分析：\n1. 驻波形成：两列振幅相等、传播方向相反的相干波叠加\n2. 瞬时能量：在波腹和波节之间来回振荡\n3. 能量流：平均坡印廷矢量为零，无净能量传播\n4. 能量特点：\n   - 电场能量和磁场能量相互转换\n   - 能量在波腹附近最大，波节附近最小\n   - 能量仅在局部区域内交换，不向外辐射\n5. 这与行波（能量持续传播）形成对比\n本题答案为正确。'
                },
                '驻波的特点包括': {
                    'content': '关于电磁波驻波的特性，以下哪些描述是正确的？（多选）\nA. 存在波腹和波节\nB. 波形不随时间传播\nC. 能量不向外传播\nD. 相位在波节处突变',
                    'options': ['A. 存在波腹和波节', 'B. 波形不传播', 'C. 能量不传播', 'D. 波节处相位突变'],
                    'explanation': '驻波的主要特征：\n1. 振幅分布：形成固定的波腹（振幅最大）和波节（振幅为零）\n2. 波形特性：波形不随时间传播，只在原地振荡\n3. 相位特点：相邻波节之间各点相位相同，波节两侧相位相反（突变π）\n4. 能量特性：能量在波腹和波节之间交换，平均能流为零\n5. 形成条件：需要反射面或边界条件限制\n以上描述均正确，答案是A、B、C、D。'
                },
                '平面电磁波是': {
                    'content': '关于均匀平面电磁波的传播特性，以下描述最准确的是：平面电磁波是（）\nA. 横电波（TE波）\nB. 横磁波（TM波）\nC. 横电磁波（TEM波）\nD. 纵波',
                    'options': ['A. 横电波(TE波)', 'B. 横磁波(TM波)', 'C. 横电磁波(TEM波)', 'D. 纵波'],
                    'explanation': '均匀平面电磁波的分类和特性：\n1. TEM波（横电磁波）：电场和磁场都垂直于传播方向\n   - 自由空间中的平面波\n   - 同轴线中的主模\n2. TE波（横电波）：电场垂直于传播方向，磁场有传播方向分量\n3. TM波（横磁波）：磁场垂直于传播方向，电场有传播方向分量\n4. 平面电磁波在自由空间中传播时是TEM波\n5. TEM波可以在双导体传输线中传播\n本题答案为C。'
                }
            }
            return self.match_enhancement(original, enhancements)

        # 第7章 导行电磁波
        elif chapter_code == 'ch7':
            enhancements = {
                '矩形波导的主模是': {
                    'content': '在矩形波导中，截止频率最低的模式称为主模。对于标准矩形波导（a > b），主模是（）\nA. TE₁₀模\nB. TE₀₁模\nC. TM₁₁模\nD. TE₂₀模',
                    'options': ['A. TE₁₀模', 'B. TE₀₁模', 'C. TM₁₁模', 'D. TE₂₀模'],
                    'explanation': '矩形波导模式分析：\n1. 截止频率公式：f_c = (c/2)√[(m/a)²+(n/b)²]\n2. 对于标准波导（a > b）：\n   - TE₁₀：f_c = c/(2a) 最低\n   - TE₂₀：f_c = c/a\n   - TE₀₁：f_c = c/(2b) > c/(2a)\n   - TM₁₁：f_c更高\n3. TE₁₀模的优点：\n   - 截止频率最低，单模工作频带宽\n   - 场结构简单，易激励\n   - 极化稳定，不易发生模式简并\n本题答案为A。'
                },
                '同轴线可以传输': {
                    'content': '关于同轴线的传输模式，以下哪种模式可以在同轴线中传输？\nA. TEM模\nB. TE₁₁模\nC. TM₀₁模\nD. 以上都可以',
                    'options': ['A. 仅TEM模', 'B. TE₁₁模', 'C. TM₀₁模', 'D. 以上都可以'],
                    'explanation': '同轴线的传输模式分析：\n1. TEM模：\n   - 截止频率为零，是主模\n   - 电场沿径向，磁场沿圆周方向\n   - 相速度等于介质中的光速\n2. TE模和TM模：\n   - 存在截止频率\n   - 当频率高于截止频率时可以传播\n   - 有色散特性\n3. 实际应用：\n   - 通常工作于TEM模（单模工作）\n   - 避免高次模以确保信号无失真传输\n同轴线可以支持TEM、TE、TM多种模式，答案是D。'
                }
            }
            return self.match_enhancement(original, enhancements)

        # 第8章 电磁辐射
        elif chapter_code == 'ch8':
            enhancements = {
                '天线增益总是大于方向性系数': {
                    'content': '关于天线增益和方向性系数的关系，以下说法是否正确：天线增益总是大于方向性系数。',
                    'explanation': '天线增益与方向性系数的关系分析：\n1. 方向性系数D：\n   - 表示天线辐射能量集中的程度\n   - 定义：D = 4πU_max/P_rad\n2. 增益G：\n   - G = η·D（η为天线效率）\n   - 考虑天线自身的欧姆损耗\n3. 效率特性：\n   - η = P_rad / P_in ≤ 1\n   - 由于损耗存在，η < 1\n   - 因此 G = ηD < D（除非理想无耗天线）\n4. 实际天线：\n   - 增益总是小于方向性系数\n   - 效率越接近1，增益越接近方向性系数\n本题答案为错误。'
                },
                '有效长度越长天线辐射越强': {
                    'content': '关于天线有效长度与辐射能力的关系，以下说法是否正确：天线的有效长度越长，其辐射能力越强。',
                    'explanation': '天线有效长度与辐射特性的关系：\n1. 有效长度定义：\n   - 将天线电流分布等效为均匀分布时的长度\n   - 反映天线将输入电流转换为辐射场的能力\n2. 辐射场强：\n   - 与有效长度成正比\n   - 有效长度越长，相同电流产生的辐射场越强\n3. 辐射功率：\n   - 与有效长度的平方成正比\n   - P_rad ∝ l_eff²\n4. 实际意义：\n   - 解释为什么长天线辐射效率更高\n   - 但需考虑阻抗匹配问题\n本题答案为正确。'
                },
                '天线增益总是大于方向性系数': {
                    'content': '关于天线增益和方向性系数的关系，以下说法是否正确：天线增益总是大于方向性系数。',
                    'explanation': '天线增益与方向性系数的关系分析：\n1. 方向性系数D：\n   - 表示天线辐射能量集中的程度\n   - 定义：D = 4πU_max/P_rad\n2. 增益G：\n   - G = η·D（η为天线效率）\n   - 考虑天线自身的欧姆损耗\n3. 效率特性：\n   - η = P_rad / P_in ≤ 1\n   - 由于损耗存在，η < 1\n   - 因此 G = ηD < D（除非理想无耗天线）\n4. 实际天线：\n   - 增益总是小于方向性系数\n   - 效率越接近1，增益越接近方向性系数\n本题答案为错误。'
                },
                '近区场和远区场特性不同': {
                    'content': '关于电偶极子辐射场的分区特性，以下说法是否正确：近区场（感应场）和远区场（辐射场）的特性不同。',
                    'explanation': '电偶极子辐射场的分区特性：\n1. 近区场（kr << 1，感应近区）：\n   - 场强∝ 1/r³ 或 1/r²\n   - 以感应场为主（静电场和静磁场的性质）\n   - 能量在源和场之间交换，不辐射\n2. 远区场（kr >> 1，辐射区）：\n   - 场强∝ 1/r\n   - 以辐射场为主（TEM波）\n   - 能量向外传播\n3. 过渡区（菲涅尔区）：\n   - 介于两者之间\n   - 两种场分量都重要\n4. 物理意义：\n   - 近区：储存能量\n   - 远区：辐射能量\n本题答案为正确。'
                },
                '常用天线类型包括': {
                    'content': '在无线通信和雷达系统中，以下哪些属于常用的天线类型？（多选）\nA. 电偶极子天线\nB. 半波振子天线\nC. 抛物面天线\nD. 微带天线',
                    'options': ['A. 电偶极子天线', 'B. 半波振子天线', 'C. 抛物面天线', 'D. 微带天线'],
                    'explanation': '常用天线类型及其应用：\n1. 电偶极子天线：\n   - 最基本的天线形式\n   - 理论分析的基础\n2. 半波振子天线：\n   - 最常用的线天线\n   - 输入阻抗约73Ω，易匹配\n3. 抛物面天线：\n   - 高增益定向天线\n   - 用于卫星通信、射电天文\n4. 微带天线：\n   - 低剖面，易共形\n   - 广泛应用于移动通信\n以上都是常用天线类型，答案是A、B、C、D。'
                },
                '天线效率与': {
                    'content': '关于天线效率的定义和影响因素，天线效率与以下哪些因素有关？（多选）\nA. 辐射电阻\nB. 损耗电阻\nC. 输入阻抗\nD. 方向性系数',
                    'options': ['A. 辐射电阻', 'B. 损耗电阻', 'C. 输入阻抗', 'D. 方向性系数'],
                    'explanation': '天线效率的定义和计算：\n1. 效率定义：\n   η = P_rad / P_in = R_rad / (R_rad + R_loss)\n2. 辐射电阻R_rad：\n   - 等效表示天线辐射能力的电阻\n   - 与天线尺寸、形状有关\n3. 损耗电阻R_loss：\n   - 导体损耗\n   - 介质损耗\n4. 影响因素：\n   - 效率取决于辐射电阻与总电阻之比\n   - 与输入阻抗、方向性系数无直接关系\n正确答案是A、B。'
                }
            }
            return self.match_enhancement(original, enhancements)

        return None

    def get_mw_content(self, chapter_code, q_type, original, options, answer):
        """获取微波工程课程的增强内容"""

        # 第1章 传输线理论
        if chapter_code == 'ch1':
            enhancements = {
                '无耗传输线的相速度等于光速': {
                    'content': '关于无耗传输线中电磁波相速度的下列说法是否正确：无耗传输线中的相速度总是等于真空中的光速。',
                    'explanation': '传输线中相速度的分析：\n1. 相速度定义：v_p = ω/β\n2. 无耗传输线：\n   β = ω√(LC)\n   v_p = 1/√(LC)\n3. 与光速的关系：\n   - 对于平行双线和同轴线：v_p = c/√ε_r\n   - 只有当ε_r = 1（空气线）时，v_p = c\n   - 一般介质填充时，v_p < c\n4. 结论：\n   - 相速度取决于传输线填充介质的介电常数\n   - 并非总是等于光速\n本题答案为错误。'
                },
                '匹配时驻波比为1': {
                    'content': '关于传输线匹配状态下的驻波比特性，以下说法是否正确：传输线匹配时，驻波比（VSWR）等于1。',
                    'explanation': '传输线匹配与驻波比的关系：\n1. 匹配定义：负载阻抗Z_L等于特性阻抗Z_0\n2. 反射系数：\n   Γ = (Z_L - Z_0)/(Z_L + Z_0)\n   匹配时Γ = 0\n3. 驻波比定义：\n   VSWR = (1+|Γ|)/(1-|Γ|)\n4. 匹配时：\n   - Γ = 0\n   - VSWR = (1+0)/(1-0) = 1\n5. 物理意义：\n   - VSWR = 1表示无反射波，只有行波\n   - 行波状态下沿线电压振幅恒定\n本题答案为正确。'
                },
                '无耗传输线的特性阻抗是实数': {
                    'content': '关于无耗传输线特性阻抗的性质，以下说法是否正确：无耗传输线的特性阻抗是纯实数。',
                    'explanation': '无耗传输线特性阻抗的分析：\n1. 特性阻抗定义：\n   Z_0 = √[(R+jωL)/(G+jωC)]\n2. 无耗传输线：\n   R = 0（无导体损耗）\n   G = 0（无介质损耗）\n3. 化简：\n   Z_0 = √(L/C)\n4. 性质分析：\n   - L和C都是正实数\n   - Z_0 = √(L/C)是正实数\n   - 与频率无关（无色散）\n5. 对比有耗线：\n   - 有耗线Z_0为复数且与频率有关\n本题答案为正确。'
                },
                '传输线长度影响输入阻抗': {
                    'content': '关于传输线输入阻抗与线长的关系，以下说法是否正确：传输线的长度会影响其输入阻抗。',
                    'explanation': '传输线输入阻抗的特性：\n1. 输入阻抗公式：\n   Z_in = Z_0·(Z_L + jZ_0tanβl)/(Z_0 + jZ_Ltanβl)\n2. 与线长的关系：\n   - 包含tanβl项，与线长l有关\n   - β = 2π/λ，是相位常数\n3. 周期性：\n   - tanβl周期为π\n   - 输入阻抗随线长周期性变化\n   - 周期为λ/2\n4. 特殊点：\n   - l = λ/4：λ/4阻抗变换特性\n   - l = λ/2：Z_in = Z_L\n5. 应用：\n   - 利用线长变化实现阻抗匹配\n   - 短路线和开路线的阻抗特性\n本题答案为正确。'
                },
                '传输线特性阻抗与': {
                    'content': '传输线的特性阻抗是传输线的重要参数，它与以下哪些因素有关？（多选）\nA. 传输线的几何结构\nB. 填充介质参数\nC. 信号频率\nD. 负载阻抗',
                    'options': ['A. 几何结构', 'B. 填充介质', 'C. 信号频率', 'D. 负载阻抗'],
                    'explanation': '传输线特性阻抗的影响因素：\n1. 基本公式（无耗线）：\n   Z_0 = √(L/C)\n2. 几何结构影响：\n   - 同轴线：Z_0 = (60/√ε_r)ln(b/a)\n   - 双线：与线径和间距有关\n   - 微带线：与宽高比有关\n3. 介质参数：\n   - ε_r影响Z_0\n   - ε_r越大，Z_0越小\n4. 频率特性：\n   - 无耗线：与频率无关\n   - 有耗线：与频率有关\n5. 负载阻抗：\n   - 只影响输入阻抗，不影响特性阻抗\n正确答案是A、B。'
                }
            }
            return self.match_enhancement(original, enhancements)

        # 第2章 史密斯圆图
        elif chapter_code == 'ch2':
            enhancements = {
                '圆图中心点反射系数为零': {
                    'content': '关于史密斯圆图的几何特性，以下说法是否正确：史密斯圆图的中心点对应反射系数为零。',
                    'explanation': '史密斯圆图中心点的含义：\n1. 圆图坐标：\n   - 横轴：归一化电阻r\n   - 纵轴：归一化电抗x\n2. 中心点位置：\n   - r = 1, x = 0\n   - 对应归一化阻抗z = 1\n3. 反射系数：\n   Γ = (z-1)/(z+1)\n   当z=1时，Γ = 0\n4. 物理意义：\n   - 匹配点\n   - VSWR = 1\n   - 无反射\n5. 应用：\n   - 阻抗匹配的靶点\n   - 匹配网络设计的目标\n本题答案为正确。'
                },
                '圆图最右端是开路点': {
                    'content': '关于史密斯圆图上特殊点的位置，以下说法是否正确：史密斯圆图的最右端是开路点。',
                    'explanation': '史密斯圆图特殊点分析：\n1. 开路点：\n   - Z_L → ∞\n   - 归一化阻抗z → ∞\n   - 位于圆图最右端\n   - Γ = 1\n2. 短路点：\n   - Z_L = 0\n   - 位于圆图最左端\n   - Γ = -1\n3. 匹配点：\n   - Z_L = Z_0\n   - 位于圆图中心\n   - Γ = 0\n4. 纯电抗圆：\n   - 位于单位圆上\n   - |Γ| = 1\n5. 旋转方向：\n   - 向信号源：顺时针\n   - 向负载：逆时针\n本题答案为正确。'
                },
                '向负载方移动逆时针': {
                    'content': '使用史密斯圆图进行阻抗分析时，关于旋转方向的规定，以下说法是否正确：在史密斯圆图上，向负载方向移动应逆时针旋转。',
                    'explanation': '史密斯圆图旋转方向规定：\n1. 旋转方向的物理意义：\n   - 沿传输线移动时阻抗的变化轨迹\n2. 向信号源移动：\n   - 远离负载，朝向信号源\n   - 顺时针旋转\n   - 一圈代表λ/2\n3. 向负载移动：\n   - 远离信号源，朝向负载\n   - 逆时针旋转\n4. 数学基础：\n   - 反射系数相位变化\n   - θ_Γ = -2βl = -4πl/λ\n   - l增加（向信号源），相位减小，顺时针\n5. 应用：\n   - 阻抗匹配设计\n   - 确定枝节位置\n本题答案为正确。'
                },
                '圆图的优点包括': {
                    'content': '史密斯圆图是微波工程中的重要工具，以下哪些是它的优点？（多选）\nA. 直观可视化\nB. 精确数值计算\nC. 图形化分析\nD. 快速估算',
                    'options': ['A. 直观可视化', 'B. 精确数值计算', 'C. 图形化分析', 'D. 快速估算'],
                    'explanation': '史密斯圆图的优点和局限性：\n1. 优点：\n   A. 直观可视化：\n      - 复平面上的阻抗、反射系数、VSWR关系一目了然\n   C. 图形化分析：\n      - 阻抗变换轨迹直观\n      - 匹配设计图形化\n   D. 快速估算：\n      - 无需复杂计算\n      - 工程近似快速有效\n2. 局限性：\n   B. 精确数值计算：\n      - 圆图精度有限\n      - 精确计算需用计算机\n3. 现代应用：\n   - 与计算机辅助设计结合\n   - 仍是理解微波概念的重要工具\n正确答案是A、C、D。'
                }
            }
            return self.match_enhancement(original, enhancements)

        # 第3章 阻抗匹配
        elif chapter_code == 'ch3':
            enhancements = {
                '匹配网络可以是纯无功网络': {
                    'content': '关于阻抗匹配网络的实现方式，以下说法是否正确：匹配网络可以由纯无功元件（电感、电容）组成。',
                    'explanation': '阻抗匹配网络的类型分析：\n1. 纯无功匹配网络：\n   - 只用电感和电容\n   - 无电阻性损耗\n   - 效率高（理想情况下100%）\n2. 实现方式：\n   - L型匹配网络\n   - π型匹配网络\n   - T型匹配网络\n   - 单/双枝节匹配\n3. 优点：\n   - 无功率损耗\n   - 保持信号质量\n4. 局限性：\n   - 带宽较窄\n   - 只能匹配特定阻抗范围\n5. 应用场景：\n   - 射频前端匹配\n   - 天线匹配网络\n本题答案为正确。'
                },
                '共轭匹配是最大功率传输条件': {
                    'content': '根据最大功率传输定理，关于共轭匹配的说法是否正确：共轭匹配是负载获得最大功率传输的条件。',
                    'explanation': '最大功率传输定理分析：\n1. 共轭匹配条件：\n   Z_L = Z_s*（负载阻抗等于源阻抗的共轭）\n2. 功率计算：\n   P = |V_s|²·R_L / [2((R_s+R_L)²+(X_s+X_L)²)]\n3. 最大功率条件：\n   - 当R_L = R_s且X_L = -X_s时\n   - 即共轭匹配\n4. 最大功率：\n   P_max = |V_s|²/(8R_s)\n5. 效率考虑：\n   - 共轭匹配时效率为50%\n   - 有时需要权衡功率和效率\n6. 应用：\n   - 射频电路设计\n   - 天线与馈线匹配\n本题答案为正确。'
                },
                '单枝节可以匹配任意阻抗': {
                    'content': '关于单枝节匹配网络的能力范围，以下说法是否正确：单枝节匹配可以匹配任意负载阻抗到传输线特性阻抗。',
                    'explanation': '单枝节匹配的能力分析：\n1. 单枝节匹配原理：\n   - 在主传输线上某位置并联（或串联）短路线/开路线\n   - 调节位置和长度实现匹配\n2. 匹配范围：\n   - 可以匹配任意复数阻抗\n   - 只要不等于特性阻抗即可\n3. 限制条件：\n   - 需要合适的线长实现\n   - 频率敏感（窄带）\n4. 双枝节匹配：\n   - 更灵活，避免"禁区"\n   - 宽带性能更好\n5. 实际考虑：\n   - 频率、带宽、物理实现限制\n   - 选择匹配网络类型需综合考虑\n本题答案为正确。'
                },
                '双枝节比单枝节更灵活': {
                    'content': '比较单枝节和双枝节匹配网络，以下说法是否正确：双枝节匹配网络比单枝节匹配网络更灵活。',
                    'explanation': '单枝节与双枝节匹配的比较：\n1. 单枝节匹配：\n   - 调节：位置d和长度l两个参数\n   - 可匹配任意阻抗\n   - 可能存在"禁区"（某些阻抗无法匹配）\n2. 双枝节匹配：\n   - 调节：两个枝节的位置和长度\n   - 更多自由度\n   - 避免单枝节的限制\n3. 双枝节优势：\n   - 固定间距，避免机械调节\n   - 更宽带宽（可设计）\n   - 某些结构中更易于实现\n4. 实际应用：\n   - 双枝节广泛用于波导和微带线\n   - 单枝节用于简单场合\n本题答案为正确。'
                },
                'λ/4变换器是窄带匹配': {
                    'content': '关于四分之一波长阻抗变换器的带宽特性，以下说法是否正确：λ/4阻抗变换器是一种窄带匹配网络。',
                    'explanation': 'λ/4阻抗变换器的带宽分析：\n1. 工作原理：\n   - 利用λ/4传输线的阻抗变换特性\n   - Z_in = Z_0²/Z_L\n2. 窄带特性原因：\n   - 只在设计频率f_0时满足λ/4条件\n   - 偏离设计频率时变换比变化\n   - tan(βl)变化导致阻抗失配\n3. 相对带宽：\n   - 通常只有10%-20%\n   - 变换比越大，带宽越窄\n4. 展宽方法：\n   - 多节λ/4变换器\n   - 渐变线（切比雪夫、二项式）\n5. 应用：\n   - 单频或窄带系统\n   - 天线馈电\n本题答案为正确。'
                }
            }
            return self.match_enhancement(original, enhancements)

        # 第4章 微波网络
        elif chapter_code == 'ch4':
            enhancements = {
                '对称网络S11=S22': {
                    'content': '关于微波网络对称性的S参数特性，以下说法是否正确：对于结构对称的微波网络，S₁₁ = S₂₂。',
                    'explanation': '网络对称性与S参数的关系：\n1. 对称网络定义：\n   - 结构上端口1和端口2对称\n   - 几何对称性\n2. S参数对称性：\n   - S₁₁ = S₂₂（输入/输出反射系数相等）\n   - 这是几何对称的直接结果\n3. 与互易性的区别：\n   - 对称性：S₁₁ = S₂₂\n   - 互易性：S₁₂ = S₂₁\n4. 判断方法：\n   - 从结构上判断是否对称\n   - 对称网络一定互易（无源）\n5. 应用：\n   - 简化网络分析\n   - 减少独立参数数量\n本题答案为正确。'
                },
                '无耗网络S矩阵是酉矩阵': {
                    'content': '关于无耗微波网络的S矩阵性质，以下说法是否正确：无耗网络的S矩阵是酉矩阵（幺正矩阵）。',
                    'explanation': '无耗网络的S矩阵性质：\n1. 无耗条件：\n   - 网络本身无能量损耗\n   - 输入功率 = 输出功率\n2. 幺正性条件：\n   S^H·S = I\n   或 S^T·S* = I\n3. 对于二端口网络：\n   |S₁₁|² + |S₂₁|² = 1\n   |S₁₂|² + |S₂₂|² = 1\n   S₁₁*S₁₂ + S₂₁*S₂₂ = 0\n4. 物理意义：\n   - 能量守恒\n   - 入射功率总和等于散射功率总和\n5. 应用：\n   - 检验网络是否无耗\n   - 简化参数测量\n本题答案为正确。'
                },
                'Z参数易在高频测量': {
                    'content': '关于微波网络参数测量方法，以下说法是否正确：Z参数（阻抗参数）容易在高频下直接测量。',
                    'explanation': '微波网络参数测量方法分析：\n1. Z参数测量：\n   - 需要开路条件\n   - 高频时开路难以实现\n   - 杂散电容影响大\n2. Y参数测量：\n   - 需要短路条件\n   - 高频时短路难以实现\n   - 引线电感影响大\n3. S参数测量：\n   - 在匹配条件下测量\n   - 使用网络分析仪\n   - 高频测量准确方便\n4. 现代微波工程：\n   - 主要使用S参数\n   - 可通过公式转换为Z、Y参数\n本题答案为错误。'
                }
            }
            return self.match_enhancement(original, enhancements)

        # 第5章 微波谐振器
        elif chapter_code == 'ch5':
            enhancements = {
                '有载Q值总是小于无载Q值': {
                    'content': '关于微波谐振器品质因数的概念，以下说法是否正确：谐振器的有载Q值总是小于无载Q值。',
                    'explanation': '谐振器Q值的关系分析：\n1. 无载Q值（Q₀）：\n   - 仅考虑谐振器本身的损耗\n   - 1/Q₀ = P_loss/(ω₀W)\n2. 外部Q值（Qₑ）：\n   - 仅考虑外部耦合损耗\n3. 有载Q值（Q_L）：\n   - 考虑总损耗\n   - 1/Q_L = 1/Q₀ + 1/Qₑ\n4. 关系推导：\n   - 因为Qₑ > 0\n   - 所以1/Q_L > 1/Q₀\n   - 因此Q_L < Q₀\n5. 物理意义：\n   - 耦合引入额外损耗\n   - 总损耗增加，Q值下降\n本题答案为正确。'
                }
            }
            return self.match_enhancement(original, enhancements)

        # 第6章 微波滤波器
        elif chapter_code == 'ch6':
            enhancements = {
                '椭圆函数滤波器在通带和阻带都有等波纹': {
                    'content': '关于椭圆函数滤波器（Cauer滤波器）的幅频特性，以下说法是否正确：椭圆函数滤波器在通带和阻带都具有等波纹特性。',
                    'explanation': '椭圆函数滤波器特性分析：\n1. 通带特性：\n   - 等波纹（等起伏）\n   - 类似切比雪夫滤波器\n2. 阻带特性：\n   - 也具有等波纹特性\n   - 这是椭圆函数滤波器的独特之处\n3. 与其他滤波器比较：\n   - 巴特沃思：通带最平坦\n   - 切比雪夫：通带等波纹，阻带单调下降\n   - 椭圆：通带和阻带都等波纹\n4. 优势：\n   - 过渡带最陡峭\n   - 相同阶数下选择性最好\n5. 代价：\n   - 相位非线性\n   - 群延迟变化大\n本题答案为正确。'
                }
            }
            return self.match_enhancement(original, enhancements)

        # 第7章 微波天线
        elif chapter_code == 'ch7':
            enhancements = {
                '天线阵方向性总是比单个单元强': {
                    'content': '关于天线阵方向性与单元方向性的关系，以下说法是否正确：天线阵的方向性总是比单个单元强。',
                    'explanation': '天线阵方向性分析：\n1. 方向性增强条件：\n   - 各单元同相激励\n   - 单元间距适当（通常λ/2左右）\n2. 方向性可能降低的情况：\n   - 反相激励\n   - 间距不当（如一个波长，出现栅瓣）\n   - 单元间耦合不良\n3. 阵列因子：\n   - 决定阵的方向性\n   - 与单元间距和激励相位有关\n4. 实际考虑：\n   - 需要优化设计\n   - 考虑扫描特性\n   - 带宽限制\n5. 结论：\n   - 方向性并非总是增强\n   - 取决于阵列设计\n本题答案为错误。'
                }
            }
            return self.match_enhancement(original, enhancements)

        # 第8章 微波系统
        elif chapter_code == 'ch8':
            enhancements = {
                '卫星通信使用微波是因为大气衰减小': {
                    'content': '关于卫星通信使用微波频段的原因，以下说法是否正确：卫星通信使用微波频段是因为该频段大气衰减相对较小。',
                    'explanation': '卫星通信频段选择分析：\n1. 大气窗口：\n   - 1-10 GHz（L、S、C、X波段）\n   - 大气吸收和衰减最小\n2. 频率过低的问题：\n   - 天线尺寸过大\n   - 频带过窄，容量有限\n3. 频率过高的问题：\n   - 雨衰严重（Ku、Ka波段）\n   - 大气吸收增加\n4. 综合考虑：\n   - 早期：C波段（4-8 GHz）\n   - 现在：Ku波段（12-18 GHz）\n   - 未来：Ka波段（26-40 GHz）\n5. 其他因素：\n   - 国际频率分配\n   - 与其他业务协调\n本题答案为正确。'
                }
            }
            return self.match_enhancement(original, enhancements)

        return None

    def match_enhancement(self, original, enhancements):
        """匹配并返回增强内容"""
        # 尝试精确匹配
        if original in enhancements:
            return enhancements[original]

        # 尝试部分匹配
        for key, value in enhancements.items():
            if key in original or original in key:
                return value

        return None
