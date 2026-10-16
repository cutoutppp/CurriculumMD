# -*- coding: utf-8 -*-
import json

with open('basic_social_courses_raw.json', 'r', encoding='utf-8') as f:
    courses = json.load(f)

out = []
for code, info in sorted(courses.items()):
    out.append('='*60)
    out.append(f"COURSE: {code}")
    out.append(f"TITLE: {info['title']}")
    text = info['full_text']
    lines = text.split('\n')
    kpi_lines = []
    capture = False
    for line in lines:
        if any(w in line for w in ['ตัวชี้วัด', 'รหัสตัวชี้วัด', 'ผลการเรียนรู้']):
            capture = True
        if capture:
            kpi_lines.append(line)
            if 'รวม' in line and ('ตัวชี้วัด' in line or 'ผลการเรียนรู้' in line):
                capture = False
    out.append('KPI SECTION:')
    for kl in kpi_lines:
        out.append('   ' + kl)

with open('basic_kpis_extracted_utf8.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))

print('Written basic_kpis_extracted_utf8.txt successfully')
