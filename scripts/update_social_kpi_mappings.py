# -*- coding: utf-8 -*-
import json
import re

THAI_TO_ARABIC = str.maketrans('๐๑๒๓๔๕๖๗๘๙', '0123456789')
def clean(t):
    return t.translate(THAI_TO_ARABIC) if t else ''

# Course code to formal name mapping for the 22 basic courses
COURSE_NAMES = {
    'ส21101': 'สังคมศึกษาฯ 1',
    'ส21102': 'ประวัติศาสตร์ 1',
    'ส21103': 'สังคมศึกษาฯ 2',
    'ส21104': 'ประวัติศาสตร์ 2',
    'ส22101': 'สังคมศึกษาฯ 3',
    'ส22102': 'ประวัติศาสตร์ 3',
    'ส22103': 'สังคมศึกษาฯ 4',
    'ส22104': 'ประวัติศาสตร์ 4',
    'ส23101': 'สังคมศึกษาฯ 5',
    'ส23102': 'ประวัติศาสตร์ 5',
    'ส23103': 'สังคมศึกษาฯ 6',
    'ส23104': 'ประวัติศาสตร์ 6',
    'ส31101': 'สังคมศึกษาฯ 1',
    'ส31102': 'ประวัติศาสตร์ 1',
    'ส31103': 'สังคมศึกษาฯ 2',
    'ส31104': 'ประวัติศาสตร์ 2',
    'ส32101': 'สังคมศึกษาฯ 3',
    'ส32102': 'ประวัติศาสตร์ 3',
    'ส32103': 'สังคมศึกษาฯ 4',
    'ส32104': 'ประวัติศาสตร์ 4',
    'ส33101': 'สังคมศึกษาฯ 5',
    'ส33102': 'สังคมศึกษาฯ 6'
}

with open('extracted_22_courses.json', 'r', encoding='utf-8') as f:
    courses = json.load(f)

def parse_course_kpis(code, raw_lines):
    kpis = []
    current_std = None
    for l in raw_lines:
        cl = clean(l).replace('–', '-').replace('—', '-').strip()
        if not cl:
            continue
        m_std = re.search(r'ส\.?\s*([1-5]\.[1-3])', cl)
        if m_std:
            current_std = f'ส {m_std.group(1)}'
        if current_std:
            items = re.findall(r'ม\.?\s*([1-6]|4-6)\s*/\s*([0-9]+(?:\s*-\s*[0-9]+)?)', cl)
            for gr, num_range in items:
                gr_str = f'ม.{gr}' if gr != '4-6' else 'ม.4-6'
                if '-' in num_range:
                    s_n, e_n = map(int, num_range.split('-'))
                    for n in range(s_n, e_n + 1):
                        kpis.append(f'{current_std} {gr_str}/{n}')
                else:
                    kpis.append(f'{current_std} {gr_str}/{int(num_range)}')
            standalone_items = re.findall(r'(?<!ม\.)(?<!ม)\b(4-6)\s*/\s*([0-9]+)', cl)
            for gr, num in standalone_items:
                kpis.append(f'{current_std} ม.4-6/{int(num)}')
    if code == 'ส21101':
        kpis.append('ส 1.2 ม.1/5')
    elif code == 'ส22103':
        kpis.append('ส 3.1 ม.2/4')
    return sorted(list(dict.fromkeys(kpis)))

course_to_kpis = {}
kpi_to_courses = {}

for code, c_data in sorted(courses.items()):
    c_name = COURSE_NAMES.get(code, c_data['name'].split()[0])
    kpi_list = parse_course_kpis(code, c_data['raw_lines'])
    course_to_kpis[code] = kpi_list
    for kp in kpi_list:
        kpi_to_courses.setdefault(kp, []).append(f"{code}_{c_name}")

print(f"Extracted {len(courses)} courses, mapped {len(kpi_to_courses)} unique KPIs.")

# 1. Update kpi_data.js
with open('kpi_data.js', 'r', encoding='utf-8') as f:
    text = f.read()

prefix = '/* Generated for Thailand Open Curriculum Portal */\nconst OPEN_CURRICULUM_DATA = '
if text.startswith(prefix):
    json_text = text[len(prefix):].rstrip().rstrip(';')
else:
    idx = text.find('{')
    json_text = text[idx:].rstrip().rstrip(';')

data = json.loads(json_text)

updated_count = 0
for k in data['kpis']:
    if k['subject'] == 'สังคมศึกษา ศาสนา และวัฒนธรรม':
        code = k['code']
        if code in kpi_to_courses:
            k['courses'] = kpi_to_courses[code]
            updated_count += 1

total_mapped = sum(1 for k in data['kpis'] if len(k.get('courses', [])) > 0)
data['total_stats']['total_mapped_kpis'] = total_mapped
if 'สังคมศึกษา ศาสนา และวัฒนธรรม' in data.get('subject_counts', {}):
    data['subject_counts']['สังคมศึกษา ศาสนา และวัฒนธรรม']['mapped'] = len(kpi_to_courses)

print(f"Updated {updated_count} Social Studies KPIs in kpi_data.js.")
print(f"New total_mapped_kpis: {total_mapped}")

new_js = f"/* Generated for Thailand Open Curriculum Portal */\nconst OPEN_CURRICULUM_DATA = {json.dumps(data, ensure_ascii=False)};"
with open('kpi_data.js', 'w', encoding='utf-8') as f:
    f.write(new_js)
print("Saved updated kpi_data.js successfully.")

# 2. Update semester_catalog.json
with open('semester_catalog.json', 'r', encoding='utf-8') as f:
    cat = json.load(f)

by_code = cat.setdefault('by_course_code', {})

# Ensure ส22104 exists
if 'ส22104' not in by_code:
    by_code['ส22104'] = {
        'code': 'ส22104',
        'name': 'ประวัติศาสตร์ 4',
        'grade': 'ม.2',
        'term': '2',
        'area': 'กลุ่มสาระการเรียนรู้สังคมศึกษา ศาสนา และวัฒนธรรม',
        'credits': 0.5,
        'hours': 20,
        'description': 'ศึกษาพัฒนาการของอาณาจักรอยุธยาและธนบุรีในด้านต่าง ๆ ปัจจัยที่ส่งผลต่อความเจริญรุ่งเรืองและความมั่นคงของอาณาจักรอยุธยา พัฒนาการด้านการเมืองการปกครอง สังคม เศรษฐกิจ และความสัมพันธ์ระหว่างประเทศ',
        'kpi_codes': [],
        'kpis_detail': [],
        'file': 'ส่วนประกอบของหลักสูตร กลุ่มสาระสังคมศึกษา ม.ต้น 2569-2571.docx'
    }

# Update all 22 basic courses
kpi_dict = {k['code']: k for k in data['kpis']}

for code, kpis in course_to_kpis.items():
    if code in by_code:
        by_code[code]['kpi_codes'] = kpis
        by_code[code]['kpis'] = kpis
        by_code[code]['kpis_count'] = len(kpis)
        by_code[code]['kpis_detail'] = [
            {
                'code': kp,
                'name': kpi_dict.get(kp, {}).get('text', ''),
                'type': kpi_dict.get(kp, {}).get('type', '')
            }
            for kp in kpis
        ]

with open('semester_catalog.json', 'w', encoding='utf-8') as f:
    json.dump(cat, f, ensure_ascii=False, indent=2)
print("Saved updated semester_catalog.json successfully.")
