from django.core.management.base import BaseCommand
from blog.models import Course, Chapter, Question


class Command(BaseCommand):
    help = '初始化题库数据'

    def handle(self, *args, **kwargs):
        def create_questions():
            em = Course.objects.get(code='electromagnetic')
            mw = Course.objects.get(code='microwave')

            # 电磁场 - 第1章 矢量分析
            ch1_em = Chapter.objects.get(course=em, code='ch1')
            questions_em_ch1 = [
                {
                    'type': 'single', 'difficulty': 1,
                    'content': '矢量分析中，梯度的运算符号是？',
                    'options': ['∇', '∇·', '∇×', '∇²'],
                    'answer': 'A',
                    'explanation': '梯度（Gradient）的运算符号是∇（nabla算子），用于表示标量场的梯度。'
                },
                {
                    'type': 'single', 'difficulty': 1,
                    'content': '两个矢量的点积结果是一个？',
                    'options': ['矢量', '标量', '张量', '矩阵'],
                    'answer': 'B',
                    'explanation': '点积（内积）的结果是一个标量。'
                },
                {
                    'type': 'single', 'difficulty': 2,
                    'content': '矢量场的旋度描述的是场的什么特性？',
                    'options': ['源的分布', '旋转性质', '梯度变化', '散度大小'],
                    'answer': 'B',
                    'explanation': '旋度（Curl）描述矢量场的旋转性质或涡旋程度。'
                },
                {
                    'type': 'judge', 'difficulty': 1,
                    'content': '标量场的梯度是一个矢量场。',
                    'options': ['正确', '错误'],
                    'answer': 'A',
                    'explanation': '标量场的梯度指向该标量场增长最快的方向，是一个矢量。'
                },
                {
                    'type': 'multiple', 'difficulty': 2,
                    'content': '矢量分析中的三个重要算子包括？',
                    'options': ['梯度', '散度', '旋度', '拉普拉斯'],
                    'answer': 'ABC',
                    'explanation': '矢量分析的三个基本算子是梯度(∇)、散度(∇·)和旋度(∇×)。'
                },
            ]

            # 电磁场 - 第2章 静电场
            ch2_em = Chapter.objects.get(course=em, code='ch2')
            questions_em_ch2 = [
                {
                    'type': 'single', 'difficulty': 1,
                    'content': '静电场中，电场强度E与电位φ的关系是？',
                    'options': ['E = ∇φ', 'E = -∇φ', 'E = ∇×φ', 'E = ∇·φ'],
                    'answer': 'B',
                    'explanation': '电场强度等于电位的负梯度，E = -∇φ。'
                },
                {
                    'type': 'single', 'difficulty': 2,
                    'content': '高斯定理的微分形式是？',
                    'options': ['∇·D = ρ', '∇×E = 0', '∇·E = 0', '∇×D = J'],
                    'answer': 'A',
                    'explanation': '高斯定理的微分形式：∇·D = ρ，表示电位移的散度等于自由电荷密度。'
                },
                {
                    'type': 'single', 'difficulty': 2,
                    'content': '静电场是？',
                    'options': ['有旋有散场', '无旋有散场', '有旋无散场', '无旋无散场'],
                    'answer': 'B',
                    'explanation': '静电场无旋（∇×E = 0）但有散（∇·D = ρ），是无旋有散场。'
                },
                {
                    'type': 'judge', 'difficulty': 1,
                    'content': '静电场中，电场线起于正电荷，止于负电荷。',
                    'options': ['正确', '错误'],
                    'answer': 'A',
                    'explanation': '静电场的电场线从正电荷发出，终止于负电荷，不会形成闭合曲线。'
                },
                {
                    'type': 'multiple', 'difficulty': 2,
                    'content': '静电场的边界条件包括？',
                    'options': ['切向E连续', '法向D连续', '切向H连续', '法向B连续'],
                    'answer': 'AB',
                    'explanation': '静电场边界条件：切向电场强度E连续，法向电位移D连续（无自由面电荷时）。'
                },
            ]

            # 电磁场 - 第3章 恒定电流场
            ch3_em = Chapter.objects.get(course=em, code='ch3')
            questions_em_ch3 = [
                {
                    'type': 'single', 'difficulty': 1,
                    'content': '欧姆定律的微分形式是？',
                    'options': ['J = σE', 'J = E/σ', 'E = σJ', 'J = ρE'],
                    'answer': 'A',
                    'explanation': '欧姆定律微分形式：J = σE，电流密度与电场强度成正比。'
                },
                {
                    'type': 'single', 'difficulty': 2,
                    'content': '恒定电流场中，电流连续性方程是？',
                    'options': ['∇·J = 0', '∇×J = 0', '∇·J = -∂ρ/∂t', '∇×J = J'],
                    'answer': 'A',
                    'explanation': '恒定电流场中，电荷分布不随时间变化，∇·J = 0。'
                },
                {
                    'type': 'judge', 'difficulty': 1,
                    'content': '恒定电流场中，电流线是闭合的。',
                    'options': ['正确', '错误'],
                    'answer': 'A',
                    'explanation': '恒定电流场中，电流线（电流密度线）是闭合的，满足连续性方程∇·J=0。'
                },
                {
                    'type': 'multiple', 'difficulty': 2,
                    'content': '恒定电流场与静电场的相似性包括？',
                    'options': ['场方程形式相似', '电位满足拉普拉斯方程', '边界条件相似', '都是时变场'],
                    'answer': 'ABC',
                    'explanation': '恒定电流场与静电场在数学形式上相似，但恒定电流场不是时变场。'
                },
            ]

            # 电磁场 - 第4章 恒定磁场
            ch4_em = Chapter.objects.get(course=em, code='ch4')
            questions_em_ch4 = [
                {
                    'type': 'single', 'difficulty': 1,
                    'content': '毕奥-萨伐尔定律描述的是？',
                    'options': ['电流产生磁场', '电荷产生电场', '变化磁场产生电场', '变化电场产生磁场'],
                    'answer': 'A',
                    'explanation': '毕奥-萨伐尔定律描述了电流元产生磁场的规律。'
                },
                {
                    'type': 'single', 'difficulty': 2,
                    'content': '恒定磁场是？',
                    'options': ['有旋有散场', '无旋有散场', '有旋无散场', '无旋无散场'],
                    'answer': 'C',
                    'explanation': '恒定磁场有旋（∇×H = J）但无散（∇·B = 0），是有旋无散场。'
                },
                {
                    'type': 'single', 'difficulty': 2,
                    'content': '安培环路定理的微分形式是？',
                    'options': ['∇×H = J', '∇·B = 0', '∇×E = -∂B/∂t', '∇·H = ρ'],
                    'answer': 'A',
                    'explanation': '安培环路定理微分形式：∇×H = J，磁场强度的旋度等于电流密度。'
                },
                {
                    'type': 'judge', 'difficulty': 1,
                    'content': '磁感应线（B线）是闭合曲线。',
                    'options': ['正确', '错误'],
                    'answer': 'A',
                    'explanation': '由于∇·B = 0，磁感应线没有起点和终点，总是闭合的。'
                },
                {
                    'type': 'multiple', 'difficulty': 2,
                    'content': '磁介质的分类包括？',
                    'options': ['抗磁质', '顺磁质', '铁磁质', '永磁质'],
                    'answer': 'ABC',
                    'explanation': '磁介质分为抗磁质、顺磁质和铁磁质三类。'
                },
            ]

            # 电磁场 - 第5章 时变电磁场
            ch5_em = Chapter.objects.get(course=em, code='ch5')
            questions_em_ch5 = [
                {
                    'type': 'single', 'difficulty': 1,
                    'content': '法拉第电磁感应定律表明？',
                    'options': ['变化电场产生磁场', '变化磁场产生电场', '电流产生磁场', '电荷产生电场'],
                    'answer': 'B',
                    'explanation': '法拉第定律：变化的磁场会产生感应电场（涡旋电场）。'
                },
                {
                    'type': 'single', 'difficulty': 2,
                    'content': '位移电流密度是？',
                    'options': ['J_d = ∂D/∂t', 'J_d = D/t', 'J_d = ∇×D', 'J_d = ∇·D'],
                    'answer': 'A',
                    'explanation': '位移电流密度 J_d = ∂D/∂t，是电位移矢量的时间变化率。'
                },
                {
                    'type': 'single', 'difficulty': 2,
                    'content': '麦克斯韦方程组中，哪个方程引入了位移电流？',
                    'options': ['∇·D = ρ', '∇×E = -∂B/∂t', '∇·B = 0', '∇×H = J + ∂D/∂t'],
                    'answer': 'D',
                    'explanation': '全电流安培定律 ∇×H = J + ∂D/∂t 中引入了位移电流项。'
                },
                {
                    'type': 'judge', 'difficulty': 2,
                    'content': '时变电磁场中，电场和磁场可以相互独立存在。',
                    'options': ['正确', '错误'],
                    'answer': 'B',
                    'explanation': '时变电磁场中，变化的电场产生磁场，变化的磁场产生电场，二者相互联系不可分割。'
                },
                {
                    'type': 'multiple', 'difficulty': 2,
                    'content': '麦克斯韦方程组包括？',
                    'options': ['∇·D = ρ', '∇×E = -∂B/∂t', '∇·B = 0', '∇×H = J + ∂D/∂t'],
                    'answer': 'ABCD',
                    'explanation': '麦克斯韦方程组包含四个方程：高斯电定律、法拉第定律、高斯磁定律和安培-麦克斯韦定律。'
                },
            ]

            # 电磁场 - 第6章 平面电磁波
            ch6_em = Chapter.objects.get(course=em, code='ch6')
            questions_em_ch6 = [
                {
                    'type': 'single', 'difficulty': 1,
                    'content': '真空中电磁波的传播速度是？',
                    'options': ['3×10^8 m/s', '3×10^6 m/s', '3×10^10 m/s', '3×10^4 m/s'],
                    'answer': 'A',
                    'explanation': '真空中光速 c = 1/√(μ₀ε₀) ≈ 3×10^8 m/s。'
                },
                {
                    'type': 'single', 'difficulty': 2,
                    'content': '平面电磁波是？',
                    'options': ['横波', '纵波', '横电波', '横磁波'],
                    'answer': 'A',
                    'explanation': '平面电磁波是横波（TEM波），电场和磁场都垂直于传播方向。'
                },
                {
                    'type': 'single', 'difficulty': 2,
                    'content': '电磁波的能流密度矢量（坡印廷矢量）方向是？',
                    'options': ['E×H', 'H×E', 'E·H', 'E+H'],
                    'answer': 'A',
                    'explanation': '坡印廷矢量 S = E×H，表示电磁波能量流动方向和大小。'
                },
                {
                    'type': 'judge', 'difficulty': 2,
                    'content': '在理想导体表面，电场强度的切向分量为零。',
                    'options': ['正确', '错误'],
                    'answer': 'A',
                    'explanation': '理想导体边界条件：切向电场为零（E_t = 0），法向磁场为零（B_n = 0）。'
                },
                {
                    'type': 'multiple', 'difficulty': 2,
                    'content': '电磁波在介质界面的反射和折射与哪些因素有关？',
                    'options': ['入射角', '极化方式', '介质电磁参数', '频率'],
                    'answer': 'ABCD',
                    'explanation': '电磁波的反射和折射特性与入射角、极化方式、介质参数（ε, μ, σ）以及频率都有关。'
                },
            ]

            # 电磁场 - 第7章 导行电磁波
            ch7_em = Chapter.objects.get(course=em, code='ch7')
            questions_em_ch7 = [
                {
                    'type': 'single', 'difficulty': 1,
                    'content': '矩形波导中不能传输的模式是？',
                    'options': ['TE10', 'TM11', 'TEM', 'TE20'],
                    'answer': 'C',
                    'explanation': '空心波导不能传输TEM模式，因为TEM模式需要两个导体。'
                },
                {
                    'type': 'single', 'difficulty': 2,
                    'content': '波导的截止频率与什么有关？',
                    'options': ['波导尺寸', '填充介质', '模式', '以上都是'],
                    'answer': 'D',
                    'explanation': '截止频率 f_c = (1/2π√με)√((mπ/a)²+(nπ/b)²)，与波导尺寸、介质和模式都有关。'
                },
                {
                    'type': 'single', 'difficulty': 2,
                    'content': '矩形波导的主模是？',
                    'options': ['TE10', 'TE01', 'TM11', 'TE11'],
                    'answer': 'A',
                    'explanation': 'TE10模是矩形波导的最低阶模式，称为主模。'
                },
                {
                    'type': 'judge', 'difficulty': 2,
                    'content': '波导中电磁波的相速度可以大于光速。',
                    'options': ['正确', '错误'],
                    'answer': 'A',
                    'explanation': '波导中相速度 v_p = ω/β > c，但群速度 v_g < c，信号传播速度不超过光速。'
                },
                {
                    'type': 'multiple', 'difficulty': 2,
                    'content': '常见的传输线类型包括？',
                    'options': ['平行双线', '同轴线', '微带线', '矩形波导'],
                    'answer': 'ABCD',
                    'explanation': '这些都是常用的微波传输线类型，适用于不同频段和场合。'
                },
            ]

            # 电磁场 - 第8章 电磁辐射
            ch8_em = Chapter.objects.get(course=em, code='ch8')
            questions_em_ch8 = [
                {
                    'type': 'single', 'difficulty': 1,
                    'content': '电偶极子辐射的远区场与距离r的关系是？',
                    'options': ['∝ 1/r', '∝ 1/r²', '∝ 1/r³', '∝ r'],
                    'answer': 'A',
                    'explanation': '远区辐射场与距离成反比（∝ 1/r），这是球面波的特征。'
                },
                {
                    'type': 'single', 'difficulty': 2,
                    'content': '天线的辐射电阻反映的是？',
                    'options': ['欧姆损耗', '辐射能力', '输入阻抗', '方向性'],
                    'answer': 'B',
                    'explanation': '辐射电阻表示天线辐射电磁能量的能力，不是实际的欧姆电阻。'
                },
                {
                    'type': 'single', 'difficulty': 2,
                    'content': '半波振子天线的长度是？',
                    'options': ['λ/4', 'λ/2', 'λ', '2λ'],
                    'answer': 'B',
                    'explanation': '半波振子天线长度为半个波长（λ/2），是最基本的天线形式。'
                },
                {
                    'type': 'judge', 'difficulty': 2,
                    'content': '近区场主要是感应场，远区场主要是辐射场。',
                    'options': ['正确', '错误'],
                    'answer': 'A',
                    'explanation': '近区（感应近区）场以感应场为主，远区（辐射区）场以辐射场为主。'
                },
                {
                    'type': 'multiple', 'difficulty': 2,
                    'content': '影响天线辐射特性的因素包括？',
                    'options': ['天线几何形状', '工作频率', '周围环境', '馈电方式'],
                    'answer': 'ABCD',
                    'explanation': '天线的辐射特性受几何形状、尺寸（相对波长）、周围环境和馈电方式等多种因素影响。'
                },
            ]

            # 微波工程 - 第1章 传输线理论
            ch1_mw = Chapter.objects.get(course=mw, code='ch1')
            questions_mw_ch1 = [
                {
                    'type': 'single', 'difficulty': 1,
                    'content': '传输线的特性阻抗与什么有关？',
                    'options': ['传输线长度', '传输线结构尺寸和介质', '信号频率', '负载阻抗'],
                    'answer': 'B',
                    'explanation': '特性阻抗 Z₀ = √(L/C)，由传输线的几何结构和填充介质决定，与长度无关。'
                },
                {
                    'type': 'single', 'difficulty': 2,
                    'content': '无耗传输线的传播常数γ是？',
                    'options': ['实数', '纯虚数', '复数', '零'],
                    'answer': 'B',
                    'explanation': '无耗线 α=0，γ = jβ，是纯虚数。'
                },
                {
                    'type': 'single', 'difficulty': 2,
                    'content': '传输线上的驻波比（VSWR）范围是？',
                    'options': ['0~1', '1~∞', '-1~1', '0~∞'],
                    'answer': 'B',
                    'explanation': 'VSWR = (1+|Γ|)/(1-|Γ|)，反射系数|Γ|∈[0,1]，所以VSWR∈[1,∞]。'
                },
                {
                    'type': 'judge', 'difficulty': 1,
                    'content': '传输线匹配时，负载阻抗等于特性阻抗。',
                    'options': ['正确', '错误'],
                    'answer': 'A',
                    'explanation': '匹配条件：Z_L = Z₀，此时反射系数为0，无反射波。'
                },
                {
                    'type': 'multiple', 'difficulty': 2,
                    'content': '传输线的工作参数包括？',
                    'options': ['特性阻抗', '传播常数', '输入阻抗', '反射系数'],
                    'answer': 'ABCD',
                    'explanation': '这些都是描述传输线工作状态的重要参数。'
                },
            ]

            # 微波工程 - 第2章 史密斯圆图
            ch2_mw = Chapter.objects.get(course=mw, code='ch2')
            questions_mw_ch2 = [
                {
                    'type': 'single', 'difficulty': 1,
                    'content': '史密斯圆图的中心点代表？',
                    'options': ['开路点', '短路点', '匹配点', '纯电抗点'],
                    'answer': 'C',
                    'explanation': '圆图中心 r=1, x=0，对应归一化阻抗为1，即匹配状态。'
                },
                {
                    'type': 'single', 'difficulty': 2,
                    'content': '在史密斯圆图上，等反射系数圆是？',
                    'options': ['同心圆', '偏心圆', '直线', '弧线'],
                    'answer': 'A',
                    'explanation': '等|Γ|圆是以原点为中心的同心圆，|Γ|越大，圆的半径越大。'
                },
                {
                    'type': 'single', 'difficulty': 2,
                    'content': '从负载向信号源移动，在圆图上应？',
                    'options': ['顺时针旋转', '逆时针旋转', '径向向内', '径向向外'],
                    'answer': 'A',
                    'explanation': '向信号源方向（远离负载）为顺时针旋转，向负载方向为逆时针旋转。'
                },
                {
                    'type': 'judge', 'difficulty': 2,
                    'content': '史密斯圆图上半圆对应容性阻抗。',
                    'options': ['正确', '错误'],
                    'answer': 'B',
                    'explanation': '上半圆x>0，对应感性阻抗；下半圆x<0，对应容性阻抗。'
                },
                {
                    'type': 'multiple', 'difficulty': 2,
                    'content': '史密斯圆图的应用包括？',
                    'options': ['阻抗匹配设计', '计算VSWR', '确定驻波相位', '分析传输线状态'],
                    'answer': 'ABCD',
                    'explanation': '史密斯圆图是微波工程的重要工具，可用于上述各种分析和设计。'
                },
            ]

            # 微波工程 - 第3章 阻抗匹配
            ch3_mw = Chapter.objects.get(course=mw, code='ch3')
            questions_mw_ch3 = [
                {
                    'type': 'single', 'difficulty': 1,
                    'content': 'λ/4阻抗变换器的特性阻抗是？',
                    'options': ['Z₀ = √(Z_in·Z_L)', 'Z₀ = Z_in + Z_L', 'Z₀ = Z_in · Z_L', 'Z₀ = Z_in / Z_L'],
                    'answer': 'A',
                    'explanation': 'λ/4变换器 Z₀ = √(Z_in·Z_L)，实现两个阻抗的变换。'
                },
                {
                    'type': 'single', 'difficulty': 2,
                    'content': '单枝节匹配可以调节的参数是？',
                    'options': ['位置和长度', '特性阻抗', '信号频率', '负载阻抗'],
                    'answer': 'A',
                    'explanation': '单枝节匹配通过调节并联（或串联）枝节的位置和长度实现匹配。'
                },
                {
                    'type': 'single', 'difficulty': 2,
                    'content': '阻抗匹配的目的是？',
                    'options': ['增大功率传输', '消除反射', '提高效率', '以上都是'],
                    'answer': 'D',
                    'explanation': '匹配可以消除反射，实现最大功率传输，提高效率。'
                },
                {
                    'type': 'judge', 'difficulty': 2,
                    'content': '共轭匹配时，负载获得最大功率。',
                    'options': ['正确', '错误'],
                    'answer': 'A',
                    'explanation': '共轭匹配（Z_L = Z_s*）是获得最大功率传输的条件。'
                },
                {
                    'type': 'multiple', 'difficulty': 2,
                    'content': '常用的阻抗匹配方法包括？',
                    'options': ['集总元件匹配', 'λ/4变换器', '枝节匹配', '渐变线匹配'],
                    'answer': 'ABCD',
                    'explanation': '这些都是常用的阻抗匹配技术，适用于不同频段和场合。'
                },
            ]

            # 微波工程 - 第4章 微波网络
            ch4_mw = Chapter.objects.get(course=mw, code='ch4')
            questions_mw_ch4 = [
                {
                    'type': 'single', 'difficulty': 1,
                    'content': '二端口网络的S参数中，S11表示？',
                    'options': ['输入反射系数', '输出反射系数', '正向传输系数', '反向传输系数'],
                    'answer': 'A',
                    'explanation': 'S11是端口2匹配时，端口1的反射系数。'
                },
                {
                    'type': 'single', 'difficulty': 2,
                    'content': '互易网络的S矩阵是？',
                    'options': ['对称矩阵', '对角矩阵', '单位矩阵', '零矩阵'],
                    'answer': 'A',
                    'explanation': '互易网络 S^T = S，S矩阵对称，Sij = Sji。'
                },
                {
                    'type': 'single', 'difficulty': 2,
                    'content': '无耗网络的S矩阵满足？',
                    'options': ['S^H·S = I', 'S^T·S = I', 'S·S = I', 'S = I'],
                    'answer': 'A',
                    'explanation': '无耗网络 S^H·S = I（幺正性），H表示共轭转置。'
                },
                {
                    'type': 'judge', 'difficulty': 2,
                    'content': 'S参数是频率的函数。',
                    'options': ['正确', '错误'],
                    'answer': 'A',
                    'explanation': 'S参数随频率变化，需要在特定频率点测量或计算。'
                },
                {
                    'type': 'multiple', 'difficulty': 2,
                    'content': '微波网络参数包括？',
                    'options': ['阻抗参数Z', '导纳参数Y', '散射参数S', '传输参数ABCD'],
                    'answer': 'ABCD',
                    'explanation': '这些都是描述微波网络的常用参数，各有适用场合。'
                },
            ]

            # 微波工程 - 第5章 微波谐振器
            ch5_mw = Chapter.objects.get(course=mw, code='ch5')
            questions_mw_ch5 = [
                {
                    'type': 'single', 'difficulty': 1,
                    'content': '谐振器的品质因数Q表示？',
                    'options': ['储能与损耗之比', '谐振频率', '带宽', '阻抗'],
                    'answer': 'A',
                    'explanation': 'Q = ω·W/P_loss，表示储能与一个周期内损耗能量之比的2π倍。'
                },
                {
                    'type': 'single', 'difficulty': 2,
                    'content': '矩形腔谐振器的谐振频率与什么有关？',
                    'options': ['腔体尺寸', '模式', '填充介质', '以上都是'],
                    'answer': 'D',
                    'explanation': '谐振频率 f = (1/2√με)√((m/a)²+(n/b)²+(p/d)²)，与尺寸、模式、介质都有关。'
                },
                {
                    'type': 'single', 'difficulty': 2,
                    'content': '圆柱腔中常用的低损耗模式是？',
                    'options': ['TE011', 'TE111', 'TM010', 'TE110'],
                    'answer': 'A',
                    'explanation': 'TE011模的壁电流沿圆周方向，损耗小，Q值高。'
                },
                {
                    'type': 'judge', 'difficulty': 2,
                    'content': '谐振器的有载Q值总是小于无载Q值。',
                    'options': ['正确', '错误'],
                    'answer': 'A',
                    'explanation': '有载Q考虑了外部耦合损耗，1/Q_L = 1/Q_0 + 1/Q_e，所以Q_L < Q_0。'
                },
                {
                    'type': 'multiple', 'difficulty': 2,
                    'content': '常见的微波谐振器类型包括？',
                    'options': ['传输线谐振器', '金属腔谐振器', '介质谐振器', '晶体谐振器'],
                    'answer': 'ABC',
                    'explanation': '这些都是微波频段常用的谐振器类型，晶体谐振器主要用于低频。'
                },
            ]

            # 微波工程 - 第6章 微波滤波器
            ch6_mw = Chapter.objects.get(course=mw, code='ch6')
            questions_mw_ch6 = [
                {
                    'type': 'single', 'difficulty': 1,
                    'content': '低通滤波器的截止频率是指？',
                    'options': ['信号完全截止的频率', '衰减达到3dB的频率', '通带中心频率', '阻带频率'],
                    'answer': 'B',
                    'explanation': '截止频率通常定义为衰减达到3dB（功率减半）的频率点。'
                },
                {
                    'type': 'single', 'difficulty': 2,
                    'content': '滤波器的插入损耗是指？',
                    'options': ['反射损耗', '传输损耗', '回波损耗', '耦合损耗'],
                    'answer': 'B',
                    'explanation': '插入损耗是信号通过滤波器后的传输损耗，IL = -10log|P_out/P_in|。'
                },
                {
                    'type': 'single', 'difficulty': 2,
                    'content': '带通滤波器的带宽是指？',
                    'options': ['3dB带宽', '6dB带宽', '通带宽度', '以上都可能'],
                    'answer': 'D',
                    'explanation': '带宽定义可以是3dB带宽、等波纹带宽等，根据设计需求而定。'
                },
                {
                    'type': 'judge', 'difficulty': 2,
                    'content': '椭圆函数滤波器在通带和阻带都有等波纹特性。',
                    'options': ['正确', '错误'],
                    'answer': 'A',
                    'explanation': '椭圆函数（Cauer）滤波器在通带和阻带都是等波纹的，过渡带最陡。'
                },
                {
                    'type': 'multiple', 'difficulty': 2,
                    'content': '常用的滤波器原型包括？',
                    'options': ['巴特沃思', '切比雪夫', '椭圆函数', '贝塞尔'],
                    'answer': 'ABCD',
                    'explanation': '这些都是经典的滤波器逼近函数，各有特点：巴特沃思最平坦，切比雪夫等波纹，椭圆最陡，贝塞尔线性相位。'
                },
            ]

            # 微波工程 - 第7章 微波天线
            ch7_mw = Chapter.objects.get(course=mw, code='ch7')
            questions_mw_ch7 = [
                {
                    'type': 'single', 'difficulty': 1,
                    'content': '天线的方向性系数D=1表示？',
                    'options': ['全向天线', '定向天线', '阵列天线', '智能天线'],
                    'answer': 'A',
                    'explanation': 'D=1表示无方向性，即全向天线（理想点源）。'
                },
                {
                    'type': 'single', 'difficulty': 2,
                    'content': '天线的增益与方向性系数的关系是？',
                    'options': ['G = D', 'G = η·D', 'G = D/η', 'G = 1/D'],
                    'answer': 'B',
                    'explanation': 'G = η·D，增益等于效率乘以方向性系数。'
                },
                {
                    'type': 'single', 'difficulty': 2,
                    'content': '半功率波束宽度（HPBW）是指？',
                    'options': ['功率降为一半的角度范围', '功率降为1/4的角度范围', '场强降为一半的角度范围',
                                '主瓣宽度'],
                    'answer': 'A',
                    'explanation': 'HPBW是辐射功率密度（场强平方）降为最大值一半（-3dB）的角度范围。'
                },
                {
                    'type': 'judge', 'difficulty': 2,
                    'content': '天线阵的方向性总是比单个单元强。',
                    'options': ['正确', '错误'],
                    'answer': 'B',
                    'explanation': '只有当天线阵各单元同相激励且间距适当时，方向性才增强；反相或间距不当可能降低。'
                },
                {
                    'type': 'multiple', 'difficulty': 2,
                    'content': '天线的主要电参数包括？',
                    'options': ['方向性', '增益', '输入阻抗', '极化'],
                    'answer': 'ABCD',
                    'explanation': '这些都是描述天线性能的基本电参数。'
                },
            ]

            # 微波工程 - 第8章 微波系统
            ch8_mw = Chapter.objects.get(course=mw, code='ch8')
            questions_mw_ch8 = [
                {
                    'type': 'single', 'difficulty': 1,
                    'content': '雷达的基本工作原理是？',
                    'options': ['发射电磁波并接收回波', '接收目标辐射', '发射连续波', '接收宇宙信号'],
                    'answer': 'A',
                    'explanation': '雷达（RADAR）通过发射电磁波并接收目标回波来探测目标。'
                },
                {
                    'type': 'single', 'difficulty': 2,
                    'content': '微波通信的主要优点是？',
                    'options': ['频带宽', '容量大', '天线小', '以上都是'],
                    'answer': 'D',
                    'explanation': '微波频段频带宽、信息容量大、波长短使天线尺寸小，都是其优点。'
                },
                {
                    'type': 'single', 'difficulty': 2,
                    'content': '微波加热的原理是？',
                    'options': ['介电损耗', '磁损耗', '欧姆损耗', '辐射损耗'],
                    'answer': 'A',
                    'explanation': '微波加热主要利用介质材料的介电损耗（极化弛豫损耗）。'
                },
                {
                    'type': 'judge', 'difficulty': 2,
                    'content': '卫星通信使用微波频段是因为大气衰减小。',
                    'options': ['正确', '错误'],
                    'answer': 'A',
                    'explanation': '微波频段（特别是1-10GHz）大气衰减和雨衰相对较小，适合卫星通信。'
                },
                {
                    'type': 'multiple', 'difficulty': 2,
                    'content': '微波技术的应用包括？',
                    'options': ['通信', '雷达', '遥感', '医疗'],
                    'answer': 'ABCD',
                    'explanation': '微波技术广泛应用于通信、雷达、遥感、医疗（微波热疗）、加热等领域。'
                },
            ]

            # 批量创建所有题目
            all_questions = []
            for chapter, questions in [
                (ch1_em, questions_em_ch1), (ch2_em, questions_em_ch2),
                (ch3_em, questions_em_ch3), (ch4_em, questions_em_ch4),
                (ch5_em, questions_em_ch5), (ch6_em, questions_em_ch6),
                (ch7_em, questions_em_ch7), (ch8_em, questions_em_ch8),
                (ch1_mw, questions_mw_ch1), (ch2_mw, questions_mw_ch2),
                (ch3_mw, questions_mw_ch3), (ch4_mw, questions_mw_ch4),
                (ch5_mw, questions_mw_ch5), (ch6_mw, questions_mw_ch6),
                (ch7_mw, questions_mw_ch7), (ch8_mw, questions_mw_ch8),
            ]:
                for q in questions:
                    Question.objects.create(
                        course=chapter.course,
                        chapter=chapter,
                        question_type=q['type'],
                        difficulty=q['difficulty'],
                        content=q['content'],
                        options=q['options'],
                        correct_answer=q['answer'],
                        explanation=q['explanation']
                    )
                    all_questions.append(q)

            print(f"成功创建 {len(all_questions)} 道题目！")
            print(
                f"电磁场：{len(questions_em_ch1) + len(questions_em_ch2) + len(questions_em_ch3) + len(questions_em_ch4) + len(questions_em_ch5) + len(questions_em_ch6) + len(questions_em_ch7) + len(questions_em_ch8)} 题")
            print(
                f"微波工程：{len(questions_mw_ch1) + len(questions_mw_ch2) + len(questions_mw_ch3) + len(questions_mw_ch4) + len(questions_mw_ch5) + len(questions_mw_ch6) + len(questions_mw_ch7) + len(questions_mw_ch8)} 题")

        create_questions()  # 添加这行
        self.stdout.write(self.style.SUCCESS('题库初始化完成！'))