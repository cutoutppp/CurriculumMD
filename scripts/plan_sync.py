import json
import os
import glob
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('school_courses_assessment_matrix.json', 'r', encoding='utf-8') as f:
    matrix = json.load(f)

vault_root = os.path.join('Curriculum_Vault', '09_หลักสูตรสถานศึกษา')
files = glob.glob(f'{vault_root}/**/*.md', recursive=True)

vault_info = {}
for vf in files:
    bn = os.path.basename(vf)
    if bn.startswith('00_'):
        continue
    m = re.match(r'^([ก-ฮa-zA-Z0-9]+)_(.*)\.md$', bn)
    code = m.group(1) if m else bn.replace('.md', '')
    fname = m.group(2) if m else ''
    
    with open(vf, 'r', encoding='utf-8') as fp:
        txt = fp.read()
    
    m_name = re.search(r'^ชื่อรายวิชา:\s*\"?([^\n\r\"]+)\"?', txt, re.M)
    name = m_name.group(1).strip() if m_name else fname
    
    # Strip any trailing period
    name = re.sub(r'\.+$', '', name).strip()
    
    # Balance parentheses if missing
    if name.count('(') > name.count(')'):
        name += ')' * (name.count('(') - name.count(')'))
        
    m_cr = re.search(r'^หน่วยกิต:\s*([0-9.]+)', txt, re.M)
    cr = float(m_cr.group(1)) if m_cr else None
    
    m_h = re.search(r'^เวลาเรียน:\s*([0-9]+)\s*ชั่วโมง', txt, re.M)
    h = int(m_h.group(1)) if m_h else None

    vault_info[code] = {
        'name': name,
        'fname': fname,
        'credits': cr,
        'hours': h,
        'path': vf
    }

print(f"Vault courses count: {len(vault_info)}")
print(f"Matrix courses count: {len(matrix)}")

# Codes in matrix to delete
to_delete = [c for c in matrix if c not in vault_info]
print("To delete from matrix:", to_delete)

# Courses with hours/credits to update
ch_updates = {}
for code, vd in vault_info.items():
    if code in matrix:
        mc = matrix[code]
        m_cr = float(mc.get('credits', 0))
        m_h = int(mc.get('total_hours', 0))
        if vd['credits'] is not None and (vd['credits'] != m_cr or vd['hours'] != m_h):
            ch_updates[code] = {
                'old_cr': m_cr, 'new_cr': vd['credits'],
                'old_h': m_h, 'new_h': vd['hours']
            }

print(f"\nCredit/hour updates ({len(ch_updates)}):")
for c, u in ch_updates.items():
    print(f"  {c}: {u['old_cr']}cr/{u['old_h']}h -> {u['new_cr']}cr/{u['new_h']}h")

# Courses with name updates
name_updates = {}
for code, vd in vault_info.items():
    if code in matrix:
        mc = matrix[code]
        m_name = mc.get('course_name', '').strip()
        v_name = vd['name'].strip()
        # Keep space in สุขศึกษา 1 / ฟิสิกส์ 7
        if v_name == 'สุขศึกษา1':
            v_name = 'สุขศึกษา 1'
        if v_name == 'ฟิสิกส์7':
            v_name = 'ฟิสิกส์ 7'
        if v_name == 'สุขศีกษาและพลศึกษา 5':
            v_name = 'สุขศึกษาและพลศึกษา 5'
        if 'การออกแบบและเทคฯ' in v_name:
            v_name = v_name.replace('การออกแบบและเทคฯ', 'การออกแบบและเทคโนโลยี')
        if m_name != v_name:
            name_updates[code] = {'old': m_name, 'new': v_name}

print(f"\nName updates ({len(name_updates)}):")
for c, u in name_updates.items():
    print(f"  {c}: '{u['old']}' -> '{u['new']}'")
