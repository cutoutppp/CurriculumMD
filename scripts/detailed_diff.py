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

vault_courses = {}
for vf in files:
    bn = os.path.basename(vf)
    if bn.startswith('00_'):
        continue
    m = re.match(r'^([ก-ฮa-zA-Z0-9]+)_(.*)\.md$', bn)
    code = m.group(1) if m else bn.replace('.md', '')
    fname = m.group(2) if m else ''
    
    with open(vf, 'r', encoding='utf-8') as fp:
        txt = fp.read()
    
    # Extract title
    m_name = re.search(r'^ชื่อรายวิชา:\s*\"?([^\n\r\"]+)\"?', txt, re.M)
    name = m_name.group(1).strip() if m_name else fname
    
    # Clean trailing dot if it's like "คณิตศาสตร์เพิ่มพูนประสบการณ์ 1."
    clean_name = re.sub(r'\.+$', '', name).strip()
    
    # Extract credit
    m_cr = re.search(r'^หน่วยกิต:\s*([0-9.]+)', txt, re.M)
    cr = float(m_cr.group(1)) if m_cr else None
    
    # Extract hours
    m_h = re.search(r'^เวลาเรียน:\s*([0-9]+)\s*ชั่วโมง', txt, re.M)
    h = int(m_h.group(1)) if m_h else None

    # Grade level
    m_g = re.search(r'^ระดับชั้น:\s*\"?([^\n\r\"]+)\"?', txt, re.M)
    grade = m_g.group(1).strip() if m_g else None
    
    vault_courses[code] = {
        'name': name,
        'clean_name': clean_name,
        'credits': cr,
        'hours': h,
        'grade': grade,
        'path': vf
    }

print(f"Total Vault courses loaded: {len(vault_courses)}")

# Compare with matrix
ch_diffs = []
name_diffs = []

for code, mc in sorted(matrix.items()):
    if code not in vault_courses:
        continue
    vc = vault_courses[code]
    
    m_cr = float(mc.get('credits', 0))
    m_h = int(mc.get('total_hours', 0))
    v_cr = vc['credits']
    v_h = vc['hours']
    
    if v_cr is not None and v_h is not None:
        if m_cr != v_cr or m_h != v_h:
            ch_diffs.append((code, mc.get('course_name'), m_cr, m_h, v_cr, v_h))
            
    m_name = mc.get('course_name', '').strip()
    v_name = vc['name'].strip()
    if m_name != v_name and m_name != vc['clean_name']:
        name_diffs.append((code, m_name, v_name, vc['clean_name']))

print(f"\nCredit/Hour diffs: {len(ch_diffs)}")
for d in ch_diffs:
    print(f"  {d[0]} {d[1]}: Matrix {d[2]}cr/{d[3]}h vs Vault {d[4]}cr/{d[5]}h")

print(f"\nName diffs (excluding trivial trailing dots): {len(name_diffs)}")
for d in name_diffs:
    print(f"  {d[0]}: Matrix '{d[1]}' vs Vault '{d[2]}'")
