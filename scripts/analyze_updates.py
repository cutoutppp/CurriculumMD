import json
import os
import glob
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('school_courses_assessment_matrix.json', 'r', encoding='utf-8') as f:
    matrix = json.load(f)

vault_root = os.path.join('Curriculum_Vault', '09_หลักสูตรสถานศึกษา')
vault_files = glob.glob(f'{vault_root}/**/*.md', recursive=True)

vault_data = {}
for vf in vault_files:
    bn = os.path.basename(vf)
    if bn.startswith('00_'):
        continue
    m = re.match(r'^([ก-ฮa-zA-Z0-9]+)_(.*)\.md$', bn)
    code = m.group(1) if m else bn.replace('.md', '')
    fname = m.group(2) if m else ''
    with open(vf, 'r', encoding='utf-8') as fp:
        txt = fp.read()
    
    m_name = re.search(r'^ชื่อรายวิชา:\s*\"?([^\n\r\"]+)\"?', txt, re.M)
    fm_name = m_name.group(1).strip() if m_name else ''
    
    m_c = re.search(r'^หน่วยกิต:\s*([0-9.]+)', txt, re.M)
    fm_cr = float(m_c.group(1)) if m_c else None
    
    m_h = re.search(r'^เวลาเรียน:\s*([0-9]+)\s*ชั่วโมง', txt, re.M)
    fm_h = int(m_h.group(1)) if m_h else None
    
    vault_data[code] = {
        'name': fm_name or fname,
        'fname': fname,
        'credits': fm_cr,
        'hours': fm_h,
        'file': vf
    }

print(f"Total Vault courses: {len(vault_data)}")
print(f"Total Matrix courses: {len(matrix)}")

# Credit/hour diffs
ch_diffs = []
for code, mc in sorted(matrix.items()):
    if code in vault_data:
        vd = vault_data[code]
        m_cr = float(mc.get('credits', 0))
        m_h = int(mc.get('total_hours', 0))
        if vd['credits'] is not None and (vd['credits'] != m_cr or vd['hours'] != m_h):
            ch_diffs.append((code, mc.get('course_name'), m_cr, m_h, vd['credits'], vd['hours']))

print(f"\nCredit/Hour Differences ({len(ch_diffs)}):")
for d in ch_diffs:
    print(f"  {d[0]} {d[1]}: Matrix={d[2]}cr/{d[3]}h -> Vault={d[4]}cr/{d[5]}h")

# Also check semester_catalog.json
with open('semester_catalog.json', 'r', encoding='utf-8') as f:
    sem_cat = json.load(f)

sem_courses = sem_cat.get('by_course_code', {})
print(f"\nTotal in semester_catalog.json by_course_code: {len(sem_courses)}")
sem_ch_diffs = []
for code, sc in sorted(sem_courses.items()):
    if code in vault_data:
        vd = vault_data[code]
        s_cr = float(sc.get('credits', 0))
        s_h = int(sc.get('total_hours', 0))
        if vd['credits'] is not None and (vd['credits'] != s_cr or vd['hours'] != s_h):
            sem_ch_diffs.append((code, sc.get('course_name'), s_cr, s_h, vd['credits'], vd['hours']))

print(f"\nCredit/Hour Differences in semester_catalog ({len(sem_ch_diffs)}):")
for d in sem_ch_diffs:
    print(f"  {d[0]} {d[1]}: SemCat={d[2]}cr/{d[3]}h -> Vault={d[4]}cr/{d[5]}h")

# Name diffs
name_diffs = []
for code, mc in sorted(matrix.items()):
    if code in vault_data:
        vd = vault_data[code]
        m_name = mc.get('course_name', '').strip()
        v_name = vd['name'].strip()
        if m_name != v_name:
            name_diffs.append((code, m_name, v_name))

print(f"\nName Differences ({len(name_diffs)}):")
for d in name_diffs:
    print(f"  {d[0]}: '{d[1]}' -> '{d[2]}'")
