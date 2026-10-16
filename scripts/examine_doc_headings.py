# -*- coding: utf-8 -*-
import docx

def examine_doc(file_path):
    print("="*80)
    print("EXAMINING:", file_path)
    print("="*80)
    doc = docx.Document(file_path)
    
    current_course = None
    collecting_kpis = False
    
    course_kpi_map = {}
    
    for i, p in enumerate(doc.paragraphs):
        t = p.text.strip()
        if not t:
            continue
            
        # Detect Course Heading
        if any(h in t for h in ['คำอธิบายรายวิชาพื้นฐาน', 'คำอธิบายรายวิชา ส', 'รายวิชาพื้นฐาน']) or ('ส2' in t or 'ส3' in t) and ('ชั้นมัธยม' in t or 'เวลา' in t or 'หน่วยกิต' in t or 'กลุ่มสาระ' in t):
            # look ahead or behind for course code
            pass
            
        if 'รหัสวิชา' in t or 'รายวิชา' in t or t.startswith('ส2') or t.startswith('ส3'):
            print(f"[P {i}] {t}")
            
examine_doc(r"school_curriculum_raw\หลักสูตรกลุ่มสาระฯ 69\สังคม 69\ส่วนประกอบของหลักสูตร กลุ่มสาระสังคมศึกษา ม.ต้น 2569-2571.docx")
examine_doc(r"school_curriculum_raw\หลักสูตรกลุ่มสาระฯ 69\สังคม 69\ส่วนประกอบของหลักสูตร กลุ่มสาระสังคมศึกษา ม.ปลาย 2569-2571.docx")
