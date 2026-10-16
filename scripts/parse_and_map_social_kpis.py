# -*- coding: utf-8 -*-
import json
import re

THAI_TO_ARABIC = str.maketrans('๐๑๒๓๔๕๖๗๘๙', '0123456789')
def clean(t):
    return t.translate(THAI_TO_ARABIC) if t else ''

with open('extracted_22_courses.json', 'r', encoding='utf-8') as f:
    courses = json.load(f)

# Load existing kpi_data.js to get all 201 secondary Social Studies KPIs
with open('kpi_data.js', 'r', encoding='utf-8') as f:
    text = f.read()

prefix = '/* Generated for Thailand Open Curriculum Portal */\nconst OPEN_CURRICULUM_DATA = '
if text.startswith(prefix):
    json_text = text[len(prefix):].rstrip().rstrip(';')
else:
    idx = text.find('{')
    json_text = text[idx:].rstrip().rstrip(';')

curriculum_data = json.loads(json_text)
kpi_list = curriculum_data.get('kpis', [])

secondary_social_kpis = {}
all_social_kpis = {}
for kpi in kpi_list:
    subj = kpi.get('subject')
    if subj == 'สังคมศึกษา ศาสนา และวัฒนธรรม':
        all_social_kpis[kpi['code']] = kpi
        grade = kpi.get('grade')
        if grade in ['ม.1', 'ม.2', 'ม.3', 'ม.4', 'ม.5', 'ม.6', 'ม.4-6']:
            secondary_social_kpis[kpi['code']] = kpi

print(f"Total Social Studies KPIs in core curriculum: {len(all_social_kpis)}")
print(f"Total secondary Social Studies KPIs in core curriculum: {len(secondary_social_kpis)}")

# Now parse indicators from each course's raw_lines
course_kpi_map = {} # course_code -> list of kpi_codes
kpi_course_map = {} # kpi_code -> list of course_codes

def parse_kpis_from_text(lines, course_code):
    extracted_kpis = []
    
    in_kpi_section = False
    current_std = None
    
    for line in lines:
        c_line = clean(line).strip()
        if not c_line:
            continue
        if any(h in c_line for h in ['รหัสตัวชี้วัด', 'ตัวชี้วัดระหว่างทาง', 'ตัวชี้วัดปลายทาง', 'ตัวชี้วัด']):
            in_kpi_section = True
            
        if not in_kpi_section:
            continue
            
        # Check standard
        m_std = re.search(r'ส\.?\s*([1-5]\.[1-3])', c_line)
        if m_std:
            current_std = f"ส {m_std.group(1)}"
            
        if current_std:
            # Pattern: ม\.?\s*([1-6]|4-6)\s*/\s*([0-9]+(?:\s*-\s*[0-9]+)?)
            items = re.findall(r'ม\.?\s*([1-6]|4-6)\s*/\s*([0-9]+(?:\s*-\s*[0-9]+)?)', c_line)
            if items:
                for gr, num_range in items:
                    gr_str = f"ม.{gr}" if gr != '4-6' else "ม.4-6"
                    if '-' in num_range:
                        start_n, end_n = map(int, num_range.split('-'))
                        for n in range(start_n, end_n + 1):
                            extracted_kpis.append(f"{current_std} {gr_str}/{n}")
                    else:
                        extracted_kpis.append(f"{current_std} {gr_str}/{int(num_range)}")
                        
    return list(dict.fromkeys(extracted_kpis))

summary = {}
for code, c_data in sorted(courses.items()):
    lines = c_data['raw_lines']
    kpis = parse_kpis_from_text(lines, code)
    course_kpi_map[code] = kpis
    for k in kpis:
        kpi_course_map.setdefault(k, []).append(code)
    summary[code] = {
        'name': c_data['name'],
        'kpi_count': len(kpis),
        'kpis': kpis
    }

print(f"Total unique KPIs mapped from 22 courses: {len(kpi_course_map)}")

# Compare with secondary_social_kpis
missing = []
for k in secondary_social_kpis:
    if k not in kpi_course_map:
        missing.append(k)

print(f"Missing from 22 courses: {len(missing)} out of {len(secondary_social_kpis)}")
with open('missing_social_kpis.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(missing))

with open('parsed_courses_summary.json', 'w', encoding='utf-8') as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)
