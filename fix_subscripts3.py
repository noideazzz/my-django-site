import re

# 第三轮替换：修正剩余教材内容中的下标
replacements = [
    ('V_out', 'Vₒᵤₜ'),
    ('I_max', 'Iᵐₐₓ'),
    ('R_f', 'Rᶠ'),
    ('G_total', 'Gₜₒₜₐₗ'),
    ('NF_total', 'NFₜₒₜₐₗ'),
    ('G_s', 'Gˢ'),
    ('Y_opt', 'Yₒₚₜ'),
    ('V_oc', 'Vₒᶜ'),
    ('I_sc', 'Iₛᶜ'),
    ('P_loss', 'Pₗₒₛₛ'),
    ('P_c', 'Pᶜ'),
    ('P_r', 'Pᵣ'),
    ('P_avs', 'Pₐᵥₛ'),
    ('P_avn', 'Pₐᵥₙ'),
    ('V_gs', 'Vᵍˢ'),
    ('V_ds', 'Vᵈˢ'),
    ('V_be', 'Vᵇᵉ'),
    ('V_ce', 'Vᶜᵉ'),
    ('I_d', 'Iᵈ'),
    ('I_dss', 'Iᵈˢˢ'),
    ('SNR_in', 'SNRᵢₙ'),
    ('SNR_out', 'SNRₒᵤₜ'),
    ('N_in', 'Nᵢₙ'),
    ('N_added', 'Nₐddₑd'),
    ('f_mnp', 'fₘₙₚ'),
    ('E_a', 'Eₐ'),
    ('e_r', 'eᵣ'),
    ('q_m', 'qₘ'),
    ('H_x', 'Hˣ'),
    ('E_y', 'Eʸ'),
    ('H_y', 'Hʸ'),
    ('E_x', 'Eˣ'),
    ('Omega_A', 'Ωₐ'),
    ('P_max', 'Pₘₐₓ'),
    ('P_avg', 'Pₐᵥg'),
    ('S_max', 'Sₘₐₓ'),
    ('dB_m', 'dBₘ'),
    ('P_1dB', 'P₁dB'),
    ('BW_3dB', 'BW₃dB'),
    ('IIP3', 'IIP₃'),
    ('OIP3', 'OIP₃'),
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
