# -*- coding: utf-8 -*-
import docx
import re
import json

def extract_all_kpis_from_docx(file_path):
    doc = docx.Document(file_path)
    
    courses = []
    current_course = None
    
    for i, p in enumerate(doc.paragraphs):
        t = p.text.strip()
        if not t:
            continue
            
        # Check course code
        # e.g., รหัส ส21101 วิชา สังคมศึกษาฯ 1
        # or รหัสวิชา ส31101
        m_code = re.search(r'รหัส\s*(?:วิชา)?\s*(ส\s*[23][0-9]{4})', t)
        if not m_code:
            m_code = re.search(r'\b(ส\s*[23][0-9]{4})\b.*?(?:วิชา|กลุ่มสาระ)', t)
            
        if m_code and any(k in t for k in ['วิชา', 'กลุ่มสาระ', 'ชั้นมัธยม']):
            code = m_code.group(1).replace(' ', '')
            current_course = {
                'code': code,
                'raw_title': t,
                'p_idx': i,
                'text_blocks': []
            }
            courses.append(current_course)
            continue
            
        if current_course:
            current_course['text_blocks'].append(t)
            
    return courses

m_ton_courses = extract_all_kpis_from_docx(r"school_curriculum_raw\หลักสูตรกลุ่มสาระฯ 69\สังคม 69\ส่วนประกอบของหลักสูตร กลุ่มสาระสังคมศึกษา ม.ต้น 2569-2571.docx")
m_plai_courses = extract_all_kpis_from_docx(r"school_curriculum_raw\หลักสูตรกลุ่มสาระฯ 69\สังคม 69\ส่วนประกอบของหลักสูตร กลุ่มสาระสังคมศึกษา ม.ปลาย 2569-2571.docx")

print(f"M.Ton raw courses: {len(m_ton_courses)}")
print(f"M.Plai raw courses: {len(m_plai_courses)}")

# Let's inspect each basic course
basic_codes = [
    'ส21101', 'ส21102', 'ส21103', 'ส21104',
    'ส22101', 'ส22102', 'ส22103', 'ส22104',
    'ส23101', 'ส23102', 'ส23103', 'ส23104',
    'ส31101', 'ส31102', 'ส31103', 'ส31104',
    'ส32101', 'ส32102', 'ส32103', 'ส32104',
    'ส33101', 'ส33102'
]

results = {}

for course_list in [m_ton_courses, m_plai_courses]:
    for c in course_list:
        code = c['code']
        if code in basic_codes:
            full_text = "\n".join(c['text_blocks'])
            # Extract KPI mentions
            # Handle forms like:
            # ส 1.1 ม.1/1
            # ม.1/2, ม1/3
            # ส.1.1
            # ส ๔.๑ ม.๒/๑
            results[code] = {
                'title': c['raw_title'],
                'full_text': full_text[:1500]
            }

with open('basic_social_courses_raw.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"Found {len(results)} basic courses. Saved to basic_social_courses_raw.json")
