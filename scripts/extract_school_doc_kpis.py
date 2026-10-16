# -*- coding: utf-8 -*-
import docx
import re

def parse_curriculum_doc(file_path):
    doc = docx.Document(file_path)
    courses = []
    
    current_course = None
    state = "SEEK" # SEEK, DESC, KPIS
    
    for i, p in enumerate(doc.paragraphs):
        t = p.text.strip()
        if not t:
            continue
            
        # Detect start of course
        # e.g., คำอธิบายรายวิชาพื้นฐาน
        # followed by รหัสวิชา ส... หรือ ส21101 สังคมศึกษาฯ 1
        m_code = re.search(r'\b(ส\s*[23][0-9]{4})\b', t)
        if m_code and any(k in t for k in ['รายวิชา', 'กลุ่มสาระ', 'ชั้นมัธยม', 'เวลา', 'ภาคเรียน', 'หน่วยกิต']):
            if current_course:
                courses.append(current_course)
            current_course = {
                'code': m_code.group(1).replace(' ', ''),
                'title_line': t,
                'p_start': i,
                'type': 'พื้นฐาน' if 'พื้นฐาน' in t else ('เพิ่มเติม' if 'เพิ่มเติม' in t else 'ไม่ระบุ'),
                'kpis': [],
                'results': [],
                'raw_kpi_lines': []
            }
            state = "DESC"
            continue
            
        # Check if previous was "คำอธิบายรายวิชาพื้นฐาน" and current line has course code
        if current_course is None and m_code:
            current_course = {
                'code': m_code.group(1).replace(' ', ''),
                'title_line': t,
                'p_start': i,
                'type': 'พื้นฐาน' if 'พื้นฐาน' in t else ('เพิ่มเติม' if 'เพิ่มเติม' in t else 'ไม่ระบุ'),
                'kpis': [],
                'results': [],
                'raw_kpi_lines': []
            }
            state = "DESC"
            continue

        if current_course:
            # Check if this paragraph contains course type if not yet known
            if 'คำอธิบายรายวิชาพื้นฐาน' in t or 'รายวิชาพื้นฐาน' in t:
                current_course['type'] = 'พื้นฐาน'
            elif 'คำอธิบายรายวิชาเพิ่มเติม' in t or 'รายวิชาเพิ่มเติม' in t:
                current_course['type'] = 'เพิ่มเติม'

            # Look for indicator section
            if 'ตัวชี้วัด' in t or 'ผลการเรียนรู้' in t:
                state = "KPIS"
                current_course['raw_kpi_lines'].append(t)
                continue
                
            if state == "KPIS":
                # Check if new course header started
                if (m_code and m_code.group(1).replace(' ', '') != current_course['code']) or 'โครงสร้างรายวิชา' in t:
                    state = "SEEK"
                    courses.append(current_course)
                    current_course = None
                    if m_code:
                        current_course = {
                            'code': m_code.group(1).replace(' ', ''),
                            'title_line': t,
                            'p_start': i,
                            'type': 'พื้นฐาน' if 'พื้นฐาน' in t else 'ไม่ระบุ',
                            'kpis': [],
                            'results': [],
                            'raw_kpi_lines': []
                        }
                        state = "DESC"
                    continue
                current_course['raw_kpi_lines'].append(t)
                
    if current_course:
        courses.append(current_course)
        
    return courses

m_ton = parse_curriculum_doc(r"school_curriculum_raw\หลักสูตรกลุ่มสาระฯ 69\สังคม 69\ส่วนประกอบของหลักสูตร กลุ่มสาระสังคมศึกษา ม.ต้น 2569-2571.docx")
m_plai = parse_curriculum_doc(r"school_curriculum_raw\หลักสูตรกลุ่มสาระฯ 69\สังคม 69\ส่วนประกอบของหลักสูตร กลุ่มสาระสังคมศึกษา ม.ปลาย 2569-2571.docx")

out = []
out.append("=== ม.ต้น COURSES FOUND ===")
for c in m_ton:
    out.append(f"Course: {c['code']} ({c['type']}) - {c['title_line'][:60]}")
    out.append(f"  KPI lines: {c['raw_kpi_lines']}")

out.append("\n=== ม.ปลาย COURSES FOUND ===")
for c in m_plai:
    out.append(f"Course: {c['code']} ({c['type']}) - {c['title_line'][:60]}")
    out.append(f"  KPI lines: {c['raw_kpi_lines']}")

with open('school_doc_extracted_courses.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))

print(f"Extracted {len(m_ton)} courses in ม.ต้น and {len(m_plai)} in ม.ปลาย.")
