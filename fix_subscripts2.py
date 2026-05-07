import re

# 第二轮替换：补充遗漏的下标
replacements = [
    # 功率相关
    ('P_loss', 'Pₗₒₛₛ'),
    ('P_c', 'Pᶜ'),
    ('P_r', 'Pᵣ'),
    ('P_avs', 'Pₐᵥₛ'),
    ('P_avn', 'Pₐᵥₙ'),
    # 电压电流
    ('V_gs', 'Vᵍˢ'),
    ('V_ds', 'Vᵈˢ'),
    ('V_be', 'Vᵇᵉ'),
    ('V_ce', 'Vᶜᵉ'),
    ('I_d', 'Iᵈ'),
    ('I_dss', 'Iᵈˢˢ'),
    # 信噪比
    ('SNR_in', 'SNRᵢₙ'),
    ('SNR_out', 'SNRₒᵤₜ'),
    ('N_in', 'Nᵢₙ'),
    ('N_added', 'Nₐddₑd'),
    # 频率模式
    ('f_mnp', 'fₘₙₚ'),
    # 场量
    ('E_a', 'Eₐ'),
    ('e_r', 'eᵣ'),
    ('q_m', 'qₘ'),
    ('I_m', 'Iᵐ'),  # 磁流
    ('H_x', 'Hˣ'),
    ('E_y', 'Eʸ'),
    ('H_y', 'Hʸ'),
    ('E_x', 'Eˣ'),
    ('H_z', 'Hᵤ'),
    # 其他
    ('Omega_A', 'Ωₐ'),
    ('P_max', 'Pₘₐₓ'),
    ('P_avg', 'Pₐᵥg'),
    ('Z_0', 'Z₀'),
    ('Z_0\'', 'Z₀\''),
    ('V_0', 'V₀'),
    ('I_0', 'I₀'),
    ('Γ_0', 'Γ₀'),
    ('f_0', 'f₀'),
    ('ω_0', 'ω₀'),
    ('λ_0', 'λ₀'),
    ('k_0', 'k₀'),
    ('β_0', 'β₀'),
    ('r_0', 'r₀'),
    ('R_0', 'R₀'),
    ('X_L', 'Xᴸ'),
    ('X_C', 'Xᶜ'),
    ('x_L', 'xᴸ'),
    ('b_C', 'bᶜ'),
    ('y_L', 'yᴸ'),
    ('z_L', 'zᴸ'),
    ('Y_s', 'Yˢ'),
    ('Z_s', 'Zˢ'),
    ('Γ_s', 'Γˢ'),
    ('Γ_opt', 'Γₒₚₜ'),
    ('R_ds', 'Rᵈˢ'),
    ('R_g', 'Rᵍ'),
    ('R_i', 'Rⁱ'),
    ('R_d', 'Rᵈ'),
    ('r_o', 'rₒ'),
    ('r_π', 'rᵖⁱ'),
    ('C_gs', 'Cᵍˢ'),
    ('C_gd', 'Cᵍᵈ'),
    ('C_ds', 'Cᵈˢ'),
    ('C_π', 'Cᵖⁱ'),
    ('C_μ', 'Cᵘ'),
    ('g_m', 'gₘ'),
    ('V_oc', 'Vₒᶜ'),
    ('I_sc', 'Iₛᶜ'),
    ('t_d', 'tᵈ'),
    ('t_r', 'tʳ'),
    ('l_eff', 'lₑff'),
    ('BW_3dB', 'BW₃dB'),
    ('dB_m', 'dBₘ'),
    ('P_1dB', 'P₁dB'),
    ('IIP3', 'IIP₃'),
    ('OIP3', 'OIP₃'),
    ('F_total', 'Fₜₒₜₐₗ'),
    ('NF_total', 'NFₜₒₜₐₗ'),
    ('S_max', 'Sₘₐₓ'),
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
    ('Q_0', 'Q₀'),
    ('Q_L', 'Qᴸ'),
    ('Q_e', 'Qᵉ'),
    ('Qc', 'Qᶜ'),
    ('Qr', 'Qᵣ'),
    ('W_e', 'Wᵉ'),
    ('W_m', 'Wᵐ'),
    ('l_e', 'lᵉ'),
    ('F_E', 'Fᴱ'),
    ('F_H', 'Fᴴ'),
    ('G_T', 'Gᵀ'),
    ('G_P', 'Gᴾ'),
    ('G_A', 'Gᴬ'),
    ('G_S', 'Gˢ'),
    ('G_L', 'Gᴸ'),
    ('G_0', 'G₀'),
    ('S_11', 'S₁₁'),
    ('S_12', 'S₁₂'),
    ('S_21', 'S₂₁'),
    ('S_22', 'S₂₂'),
    ('η_a', 'ηₐ'),
    ('F_min', 'Fₘᵢₙ'),
    ('T_0', 'T₀'),
    ('T_e', 'Tᵉ'),
    ('k_c', 'kᶜ'),
    ('β_z', 'βᵤ'),
    ('v_px', 'vᵖˣ'),
    ('λ_c', 'λᶜ'),
    ('λ_g', 'λᵍ'),
    ('f_c', 'fᶜ'),
    ('Z_L', 'Zᴸ'),
    ('Z_in', 'Zᵢₙ'),
    ('Γ_L', 'Γᴸ'),
    ('R_r', 'Rᵣ'),
    ('R_s', 'Rˢ'),
    ('R_l', 'Rˡ'),
    ('R_b', 'Rᵇ'),
    ('R_n', 'Rⁿ'),
    ('V_cc', 'Vᶜᶜ'),
    ('V_dd', 'Vᵈᵈ'),
    ('I_c', 'Iᶜ'),
    ('I_m', 'Iᵐ'),
    ('V_m', 'Vᵐ'),
    ('P_in', 'Pᵢₙ'),
    ('P_out', 'Pₒᵤₜ'),
    ('P_dc', 'Pᵈᶜ'),
    ('P_L', 'Pᴸ'),
    ('P_R', 'Pᴿ'),
    ('P_T', 'Pᵀ'),
    ('f_T', 'fᵀ'),
    ('f_max', 'fₘₐₓ'),
]

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    for old, new in replacements:
        content = content.replace(old, new)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
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
