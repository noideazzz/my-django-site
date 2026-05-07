import re
import sys

# 定义替换规则（下标替换为Unicode下标）
# 注意：需要避免在HTML标签内部进行替换

replacements = [
    # 辐射电阻
    ('R_r', 'Rᵣ'),
    # 截止频率
    ('f_c', 'fᶜ'),
    # 负载阻抗
    ('Z_L', 'Zᴸ'),
    # 输入阻抗
    ('Z_in', 'Zᵢₙ'),
    # 源阻抗
    ('Z_S', 'Zˢ'),
    # 相速
    ('v_p', 'vᵖ'),
    ('vₚ', 'vᵖ'),  # 修正已有的
    # 群速
    ('v_g', 'vᵍ'),
    ('v₉', 'vᵍ'),  # 修正已有的
    # 反射系数
    ('Γ_L', 'Γᴸ'),
    # 电场
    ('E_r', 'Eᵣ'),
    ('E_i', 'Eᵢ'),
    ('E_t', 'Eᵗ'),
    # 纵向分量
    ('E_z', 'Eᵤ'),
    ('H_z', 'Hᵤ'),
    # 电流电压
    ('I_c', 'Iᶜ'),
    ('V_cc', 'Vᶜᶜ'),
    ('V_dd', 'Vᵈᵈ'),
    ('I_m', 'Iᵐ'),
    ('V_m', 'Vᵐ'),
    # 功率
    ('P_in', 'Pᵢₙ'),
    ('P_out', 'Pₒᵤₜ'),
    ('P_dc', 'Pᵈᶜ'),
    ('P_L', 'Pᴸ'),
    ('P_R', 'Pᴿ'),
    ('P_T', 'Pᵀ'),
    # 频率
    ('f_T', 'fᵀ'),
    ('f_max', 'fₘₐₓ'),
    # 电阻
    ('R_s', 'Rˢ'),
    ('R_l', 'Rˡ'),
    ('R_b', 'Rᵇ'),
    ('R_n', 'Rⁿ'),
    # 电容
    ('C_π', 'Cᵖⁱ'),
    ('C_μ', 'Cᵘ'),
    ('C_gs', 'Cᵍˢ'),
    ('C_gd', 'Cᵍᵈ'),
    ('C_ds', 'Cᵈˢ'),
    # 跨导
    ('g_m', 'gₘ'),
    # 其他
    ('r_π', 'rᵖⁱ'),
    ('t_d', 'tᵈ'),
    ('t_r', 'tʳ'),
    ('Q_0', 'Q₀'),
    ('Q_L', 'Qᴸ'),
    ('Q_e', 'Qᵉ'),
    ('W_e', 'Wᵉ'),
    ('W_m', 'Wᵐ'),
    ('l_e', 'lᵉ'),
    ('l_eff', 'lₑff'),
    # 方向图
    ('F_E', 'Fᴱ'),
    ('F_H', 'Fᴴ'),
    # 增益
    ('G_T', 'Gᵀ'),
    ('G_P', 'Gᴾ'),
    ('G_A', 'Gᴬ'),
    ('G_S', 'Gˢ'),
    ('G_L', 'Gᴸ'),
    ('G_0', 'G₀'),
    # S参数
    ('S_11', 'S₁₁'),
    ('S_12', 'S₁₂'),
    ('S_21', 'S₂₁'),
    ('S_22', 'S₂₂'),
    # 其他阻抗
    ('Z_0', 'Z₀'),
    ('Z_L', 'Zᴸ'),
    # 电压电流
    ('V_0', 'V₀'),
    ('I_0', 'I₀'),
    ('V_S', 'Vˢ'),
    ('V_L', 'Vᴸ'),
    # 其他下标
    ('Z_in', 'Zᵢₙ'),
    ('Y_s', 'Yˢ'),
    ('Z_s', 'Zˢ'),
    ('Γ_s', 'Γˢ'),
    ('Γ_L', 'Γᴸ'),
    ('Γ_0', 'Γ₀'),
    ('Γ_opt', 'Γₒₚₜ'),
    ('R_ds', 'Rᵈˢ'),
    ('R_g', 'Rᵍ'),
    ('R_i', 'Rⁱ'),
    ('R_d', 'Rᵈ'),
    ('r_o', 'rₒ'),
    ('x_L', 'xᴸ'),
    ('b_C', 'bᶜ'),
    ('y_L', 'yᴸ'),
    ('z_L', 'zᴸ'),
    ('p_m', 'pₘ'),
    ('p_mn', 'pₘₙ'),
    ('TE_10', 'TE₁₀'),
    ('TE_11', 'TE₁₁'),
    ('TE_01', 'TE₀₁'),
    ('TE_21', 'TE₂₁'),
    ('TM_01', 'TM₀₁'),
    ('TM_11', 'TM₁₁'),
    ('TM_mn', 'TMₘₙ'),
    ('TE_mn', 'TEₘₙ'),
    ('TM_mnp', 'TMₘₙₚ'),
    ('TE_mnp', 'TEₘₙₚ'),
    # 效率
    ('η_a', 'ηₐ'),
    # 噪声
    ('F_min', 'Fₘᵢₙ'),
    ('T_0', 'T₀'),
    ('T_e', 'Tᵉ'),
    # 其他
    ('k_c', 'kᶜ'),
    ('β_z', 'βᵤ'),
    ('v_px', 'vᵖˣ'),
    ('λ_c', 'λᶜ'),
    ('λ_g', 'λᵍ'),
    ('λ_0', 'λ₀'),
    ('f_0', 'f₀'),
    ('ω_0', 'ω₀'),
    ('BW_3dB', 'BW₃dB'),
    ('dB_m', 'dBₘ'),
    ('P_1dB', 'P₁dB'),
    ('IIP3', 'IIP₃'),
    ('OIP3', 'OIP₃'),
    ('V_oc', 'Vₒᶜ'),
    ('I_sc', 'Iₛᶜ'),
]

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # 对每一对替换规则进行处理
    for old, new in replacements:
        # 使用正则表达式，确保只替换不在HTML标签内的内容
        # 简单处理：直接替换
        content = content.replace(old, new)
    
    # 写入文件
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # 统计替换次数
    changes = sum(1 for a, b in zip(original, content) if a != b)
    return changes

if __name__ == '__main__':
    files = [
        'e:\\Program Files\\Trae\\DjangoProject2_trae\\templates\\knowledge_ee.html',
        'e:\\Program Files\\Trae\\DjangoProject2_trae\\templates\\knowledge_mw.html'
    ]
    
    for filepath in files:
        try:
            changes = fix_file(filepath)
            print(f'已处理: {filepath}')
            print(f'  字符变化数: {changes}')
        except Exception as e:
            print(f'处理失败: {filepath}')
            print(f'  错误: {e}')
