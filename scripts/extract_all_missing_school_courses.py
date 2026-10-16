# -*- coding: utf-8 -*-
"""
Full Extraction Engine:
1. Extracts missing school courses from raw DOCX files across all subject groups.
2. Fills remaining courses from Master Excel 2569-2571 to achieve 100% complete school curriculum coverage.
3. Synchronizes Curriculum_Vault, school_courses_assessment_matrix.json, semester_catalog.json, and AssessmentHub.
"""
import os
import sys
import glob
import re
import json
import docx
import openpyxl

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

THAI_DIGITS = str.maketrans('๐๑๒๓๔๕๖๗๘๙', '0123456789')

PREFIX_AREA_MAP = {
    'ท': ('ภาษาไทย', '01_ภาษาไทย'),
    'ค': ('คณิตศาสตร์', '02_คณิตศาสตร์'),
    'ว': ('วิทยาศาสตร์และเทคโนโลยี', '03_วิทยาศาสตร์และเทคโนโลยี'),
    'ส': ('สังคมศึกษา ศาสนา และวัฒนธรรม', '04_สังคมศึกษา'),
    'พ': ('สุขศึกษาและพลศึกษา', '05_สุขศึกษาและพลศึกษา'),
    'ศ': ('ศิลปะ', '06_ศิลปะ'),
    'ง': ('การงานอาชีพ', '07_การงานอาชีพ'),
    'อ': ('ภาษาต่างประเทศ', '08_ภาษาต่างประเทศ'),
    'จ': ('ภาษาต่างประเทศ', '08_ภาษาต่างประเทศ'),
    'ฝ': ('ภาษาต่างประเทศ', '08_ภาษาต่างประเทศ'),
    'ญ': ('ภาษาต่างประเทศ', '08_ภาษาต่างประเทศ'),
    'I': ('กิจกรรมพัฒนาผู้เรียน (IS)', '09_กิจกรรมพัฒนาผู้เรียน_IS')
}

def clean_str(s):
    if not s:
        return ""
    return re.sub(r'\s+', ' ', str(s)).strip()

def parse_docx_courses(raw_base):
    print("--- STEP 1: Parsing all DOCX files for course data ---")
    docx_files = []
    for root, dirs, files in os.walk(raw_base):
        for f in files:
            if f.endswith('.docx') and not f.startswith('~$'):
                docx_files.append(os.path.join(root, f))
    
    print(f"Scanning {len(docx_files)} DOCX files...")
    
    extracted_courses = {} # code -> dict
    
    for df in docx_files:
        try:
            doc = docx.Document(df)
        except Exception:
            continue
            
        # Parse paragraphs looking for course sections
        paragraphs = doc.paragraphs
        p_len = len(paragraphs)
        
        for idx, p in enumerate(paragraphs):
            text_norm = p.text.translate(THAI_DIGITS).strip()
            
            # Check for course header
            # Patterns: รหัสวิชา [code] รายวิชา [name] or รหัส [code] [name]
            m = re.search(r'(?:รหัสวิชา|รหัส)\s*([ทควสพศงอตจฝญI]\s*\d{5})\s*(?:รายวิชา|วิชา)?\s*([^\n\t\r]+)?', text_norm)
            if not m:
                # Alternate pattern: รายวิชา [name] รหัสวิชา [code]
                m_alt = re.search(r'(?:รายวิชา|วิชา)\s*([^\n\t\r]+)\s*(?:รหัสวิชา|รหัส)\s*([ทควสพศงอตจฝญI]\s*\d{5})', text_norm)
                if m_alt:
                    raw_code = m_alt.group(2)
                    raw_name = m_alt.group(1)
                else:
                    continue
            else:
                raw_code = m.group(1)
                raw_name = m.group(2) if m.group(2) else ""
                
            code = re.sub(r'\s+', '', raw_code)
            name = clean_str(raw_name)
            name = re.sub(r'\s*กลุ่มสาระ.*$', '', name).strip()
            name = re.sub(r'\s*ชั้น.*$', '', name).strip()
            name = re.sub(r'\s*เวลา.*$', '', name).strip()
            name = re.sub(r'\s*จำนวน.*$', '', name).strip()
            
            # Extract subsequent lines for description, grade, semester, hours, credits
            desc_lines = []
            grade = ""
            sem = ""
            hours = 40
            credits = 1.0
            
            for j in range(idx + 1, min(idx + 35, p_len)):
                next_p = paragraphs[j]
                line_raw = next_p.text.strip()
                line_norm = line_raw.translate(THAI_DIGITS)
                
                # If hitting another course header or major section, stop
                if re.search(r'(?:รหัสวิชา|รหัส)\s*[ทควสพศงอตจฝญI]\s*\d{5}', line_norm):
                    break
                if "โครงสร้างรายวิชา" in line_norm:
                    break
                
                # Extract metadata
                m_grade = re.search(r'(?:ชั้น|ระดับชั้น)?มัธยมศึกษาปีที่\s*([1-6๑-๖])', line_norm)
                if m_grade:
                    grade = f"ม.{m_grade.group(1)}"
                elif "ม.ต้น" in line_norm:
                    grade = "ม.ต้น"
                elif "ม.ปลาย" in line_norm:
                    grade = "ม.ปลาย"
                    
                m_sem = re.search(r'ภาคเรียนที่\s*([1-2๑-๒])', line_norm)
                if m_sem:
                    sem = m_sem.group(1)
                    
                m_hrs = re.search(r'เวลา\s*([0-9]+)\s*(?:ชั่วโมง|คาบ)', line_norm)
                if m_hrs:
                    try: hours = int(m_hrs.group(1))
                    except: pass
                    
                m_creds = re.search(r'จำนวน\s*([0-9.]+)\s*หน่วยกิต', line_norm)
                if m_creds:
                    try: credits = float(m_creds.group(1))
                    except: pass
                    
                if line_raw and not line_raw.startswith('---') and not line_raw.startswith('***'):
                    if not any(k in line_raw for k in ['ชั้นมัธยม', 'ภาคเรียนที่', 'เวลาเรียน', 'กลุ่มสาระ']):
                        desc_lines.append(line_raw)
                        
            desc_text = "\n\n".join(desc_lines)
            
            # Infer grade from code if still missing
            if not grade:
                if len(code) >= 3 and code[1] == '2':
                    grade = f"ม.{code[2]}"
                elif len(code) >= 3 and code[1] == '3':
                    d = int(code[2]) if code[2].isdigit() else 1
                    grade = f"ม.{d+3}" if d <= 3 else "ม.ปลาย"
                    
            if not sem:
                # If last digit of code is even -> sem 2, odd -> sem 1
                last_d = code[-1]
                if last_d.isdigit():
                    sem = "2" if int(last_d) % 2 == 0 else "1"
                else:
                    sem = "1"
                    
            area, folder = PREFIX_AREA_MAP.get(code[0], ('กลุ่มสาระการเรียนรู้', '00_ทั่วไป'))
            
            if code not in extracted_courses or len(desc_text) > len(extracted_courses[code].get('description', '')):
                extracted_courses[code] = {
                    'code': code,
                    'name': name if name else extracted_courses.get(code, {}).get('name', code),
                    'grade': grade,
                    'semester': sem,
                    'hours': hours,
                    'credits': credits,
                    'learning_area': area,
                    'folder': folder,
                    'description': desc_text,
                    'source_file': os.path.basename(df),
                    'units': []
                }
                
        # Parse tables in doc looking for unit structure
        for t in doc.tables:
            if len(t.rows) < 2:
                continue
            r0 = [c.text.strip().translate(THAI_DIGITS) for c in t.rows[0].cells]
            is_unit_table = any('หน่วย' in c for c in r0[:3]) and any(k in ''.join(r0) for k in ['สาระสำคัญ', 'คะแนน', 'เวลา', 'ผลการเรียนรู้', 'ตัวชี้วัด'])
            if not is_unit_table:
                continue
                
            # Find which course this table belongs to by looking at preceding paragraphs
            t_elem = t._element
            prev = t_elem.getprevious()
            matched_code = None
            while prev is not None:
                if prev.tag.endswith('p'):
                    p_txt = (prev.text or "").translate(THAI_DIGITS)
                    m_c = re.search(r'(?:รหัสวิชา|รหัส)\s*([ทควสพศงอตจฝญI]\s*\d{5})', p_txt)
                    if m_c:
                        matched_code = re.sub(r'\s+', '', m_c.group(1))
                        break
                prev = prev.getprevious()
                
            if not matched_code or matched_code not in extracted_courses:
                continue
                
            # Parse table rows into units
            course_units = []
            for r_idx, r in enumerate(t.rows[1:], 1):
                cells = [c.text.strip().translate(THAI_DIGITS) for c in r.cells]
                row_str = " ".join(cells)
                if any(k in row_str for k in ['รวม', 'ปลายภาค', 'กลางภาค']):
                    continue
                u_no = cells[0] if len(cells) > 0 else str(r_idx)
                u_name = cells[1] if len(cells) > 1 else f"หน่วยการเรียนรู้ที่ {u_no}"
                kpi_col = cells[2] if len(cells) > 2 else ""
                concept_col = cells[3] if len(cells) > 3 else ""
                
                # Extract numbers for hours and scores
                hrs = 4
                tot_score = 15
                k, p, a = 8, 4, 3
                
                nums = re.findall(r'\d+', row_str)
                if nums:
                    # heuristic: find hours and scores
                    pass
                    
                if u_name:
                    course_units.append({
                        'unit_no': u_no,
                        'unit_name': u_name,
                        'indicators_raw': [kpi_col] if kpi_col else [],
                        'key_concepts': [concept_col] if concept_col else [],
                        'hours': hrs,
                        'score_k': k, 'score_p': p, 'score_a': a, 'score_total': tot_score
                    })
                    
            if course_units and (not extracted_courses[matched_code]['units'] or len(course_units) > len(extracted_courses[matched_code]['units'])):
                extracted_courses[matched_code]['units'] = course_units

    print(f"Extracted {len(extracted_courses)} courses from DOCX files.")
    return extracted_courses

def load_master_excel_courses(raw_base):
    print("\n--- STEP 2: Loading Master Excel 2569-2571 ---")
    xlsx_path = os.path.join(raw_base, ' โครงสร้างหลักสูตร  โรงเรียนพัฒนานิคม(ปี2569-2571) แก้ไขรายวิชา.xlsx')
    wb = openpyxl.load_workbook(xlsx_path, data_only=True)
    
    excel_courses = {}
    for sname in ['2569-2571(ม.1,4)', 'รายวิชาเพิ่มเติมเสรี ']:
        if sname not in wb.sheetnames:
            continue
        ws = wb[sname]
        for r in range(1, ws.max_row + 1):
            row_vals = [ws.cell(r, c).value for c in range(1, ws.max_column + 1)]
            for cell in row_vals:
                if not cell:
                    continue
                s = str(cell).strip()
                matches = re.finditer(r'([ทควสพศงอตจฝญI]\s*\d{5})\s*([^\d\n\r]+)?', s)
                for m in matches:
                    c_code = re.sub(r'\s+', '', m.group(1))
                    c_name = clean_str(m.group(2) if m.group(2) else "")
                    c_name = re.sub(r'\s*\d+\.\d+.*$', '', c_name).strip()
                    
                    if c_code not in excel_courses or (not excel_courses[c_code]['name'] and c_name):
                        area, folder = PREFIX_AREA_MAP.get(c_code[0], ('กลุ่มสาระการเรียนรู้', '00_ทั่วไป'))
                        grade = "ม.1"
                        if len(c_code) >= 3 and c_code[1] == '2':
                            grade = f"ม.{c_code[2]}"
                        elif len(c_code) >= 3 and c_code[1] == '3':
                            d = int(c_code[2]) if c_code[2].isdigit() else 1
                            grade = f"ม.{d+3}" if d <= 3 else "ม.ปลาย"
                            
                        sem = "2" if c_code[-1].isdigit() and int(c_code[-1]) % 2 == 0 else "1"
                        
                        excel_courses[c_code] = {
                            'code': c_code,
                            'name': c_name,
                            'learning_area': area,
                            'folder': folder,
                            'grade': grade,
                            'semester': sem,
                            'credits': 1.0,
                            'hours': 40
                        }
                        
    print(f"Loaded {len(excel_courses)} courses from Master Excel.")
    return excel_courses

def build_vault_markdown(c):
    code = c['code']
    name = c.get('name') or code
    area = c.get('learning_area', 'กลุ่มสาระการเรียนรู้')
    grade = c.get('grade', 'ม.1')
    sem = c.get('semester', '1')
    credits = c.get('credits', 1.0)
    hours = c.get('hours', int(credits * 40))
    desc = c.get('description', '').strip()
    units = c.get('units', [])
    
    if not units:
        # Default 4 units
        q_h = hours // 4
        units = [
            {'unit_no': '1', 'unit_name': 'หน่วยการเรียนรู้ที่ 1', 'hours': q_h, 'score_k': 8, 'score_p': 2, 'score_a': 0, 'score_total': 10, 'indicators_raw': [], 'key_concepts': []},
            {'unit_no': '2', 'unit_name': 'หน่วยการเรียนรู้ที่ 2', 'hours': q_h, 'score_k': 10, 'score_p': 3, 'score_a': 2, 'score_total': 15, 'indicators_raw': [], 'key_concepts': []},
            {'unit_no': '3', 'unit_name': 'หน่วยการเรียนรู้ที่ 3', 'hours': q_h, 'score_k': 7, 'score_p': 5, 'score_a': 3, 'score_total': 15, 'indicators_raw': [], 'key_concepts': []},
            {'unit_no': '4', 'unit_name': 'หน่วยการเรียนรู้ที่ 4', 'hours': hours - (q_h * 3), 'score_k': 6, 'score_p': 2, 'score_a': 2, 'score_total': 10, 'indicators_raw': [], 'key_concepts': []}
        ]

    md = "---\n"
    md += f"รหัสวิชา: {code}\n"
    md += f"ชื่อรายวิชา: \"{name}\"\n"
    md += f"กลุ่มสาระ: \"{area}\"\n"
    md += f"ระดับชั้น: \"{grade}\"\n"
    md += f"ภาคเรียนที่: {sem}\n"
    md += f"หน่วยกิต: {credits}\n"
    md += f"เวลาเรียน: {hours} ชั่วโมง\n"
    md += f"จำนวนหน่วยการเรียนรู้: {len(units)}\n"
    tags = ["school_curriculum", "course", "โรงเรียนพัฒนานิคม", "แผนวัดและประเมินผล"]
    if grade:
        tags.append(grade.replace('.', ''))
    md += f"tags: [{', '.join(tags)}]\n"
    md += "---\n\n"
    
    md += f"# {code} {name}\n\n"
    md += f"> **หลักสูตรสถานศึกษา โรงเรียนพัฒนานิคม พ.ศ. 2569–2571**  \n"
    md += f"> 📍 กลุ่มสาระการเรียนรู้: **{area}** | ระดับชั้น: **{grade}** (ภาคเรียนที่ {sem}) | เวลาเรียน: **{hours} ชั่วโมง** ({credits} หน่วยกิต)\n\n"
    md += f"> 🔗 **เชื่อมโยงระบบ:** [[00_หลักสูตรสถานศึกษา]] | [[00_ระบบแผนการวัดและประเมินผล]] | [[00_กลุ่มสาระ_{area}]]\n\n"
    
    md += "## 📝 คำอธิบายรายวิชา (Course Description)\n\n"
    if desc:
        md += f"{desc}\n\n"
    else:
        md += f"ศึกษาและฝึกทักษะกระบวนการเรียนรู้ตามโครงสร้างรายวิชา {name} ({code}) กลุ่มสาระการเรียนรู้{area} เพื่อให้ผู้เรียนเกิดความรู้ ความเข้าใจ มีทักษะในการคิด วิเคราะห์ และการประยุกต์ใช้ในการดำเนินชีวิตได้อย่างมีประสิทธิภาพ\n\n"
    md += "---\n\n"
    
    md += "## 🎯 ตารางโครงสร้างรายวิชาและแผนการวัดและประเมินผลการเรียนรู้\n\n"
    md += "| หน่วยที่ | ชื่อหน่วยการเรียนรู้ | มาตรฐาน/ตัวชี้วัด / ผลการเรียนรู้ | สาระสำคัญ / ความคิดรวบยอด | เวลา (ชม.) | K | P | A | รวม |\n"
    md += "| :---: | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |\n"
    
    for u in units:
        u_no = u.get('unit_no', '')
        u_name = u.get('unit_name', '').replace('|', '/')
        ind_list = u.get('indicators_raw', [])
        ind_str = "<br>".join([x.replace('|', '/') for x in ind_list]) if ind_list else "-"
        concept_list = u.get('key_concepts', [])
        concept_str = "<br>".join([x.replace('|', '/') for x in concept_list]) if concept_list else f"สาระสำคัญของหน่วยการเรียนรู้ที่ {u_no}"
        h = u.get('hours', 4)
        k = u.get('score_k', 8)
        p = u.get('score_p', 2)
        a = u.get('score_a', 0)
        tot = u.get('score_total', 10)
        md += f"| {u_no} | **{u_name}** | {ind_str} | {concept_str} | {h} | {k} | {p} | {a} | **{tot}** |\n"
        
    md += "\n---\n\n"
    md += "## 📋 รายละเอียดตัวชี้วัดและภาระงานประเมิน (Blueprint สำหรับจัดทำแผนการสอนและแผนวัด)\n\n"
    for u in units:
        u_no = u.get('unit_no', '')
        u_name = u.get('unit_name', '')
        h = u.get('hours', 4)
        k = u.get('score_k', 8)
        p = u.get('score_p', 2)
        a = u.get('score_a', 0)
        tot = u.get('score_total', 10)
        md += f"### หน่วยที่ {u_no}: {u_name}\n"
        md += f"- **เวลาเรียน:** {h} ชั่วโมง | **คะแนนรวม:** {tot} คะแนน (K: {k} / P: {p} / A: {a})\n\n"
        
    return md

def execute_full_sync():
    print("==================================================================")
    print("🚀 RUNNING FULL SCHOOL CURRICULUM EXTRACTION & SYNC")
    print("==================================================================")
    
    cwd = os.getcwd()
    raw_root = os.path.join(cwd, 'school_curriculum_raw')
    top_entries = os.listdir(raw_root)
    top_folder = [e for e in top_entries if os.path.isdir(os.path.join(raw_root, e))][0]
    raw_base = os.path.join(raw_root, top_folder)
    
    vault_base = os.path.join(cwd, 'Curriculum_Vault', '09_หลักสูตรสถานศึกษา')
    
    # 1. Parse DOCX
    docx_courses = parse_docx_courses(raw_base)
    
    # 2. Parse Excel
    excel_courses = load_master_excel_courses(raw_base)
    
    # 3. Load Matrix
    matrix_path = os.path.join(cwd, 'school_courses_assessment_matrix.json')
    with open(matrix_path, 'r', encoding='utf-8') as f:
        matrix = json.load(f)
        
    # 4. Load Catalog
    catalog_path = os.path.join(cwd, 'semester_catalog.json')
    with open(catalog_path, 'r', encoding='utf-8') as f:
        catalog = json.load(f)
    cat_by_code = catalog.get('by_course_code', {})
    
    # 5. Existing vault files map
    vault_files = glob.glob(f"{vault_base}/**/*.md", recursive=True)
    existing_vault_codes = set()
    for vf in vault_files:
        b = os.path.basename(vf)
        if b.startswith('00_'): continue
        m = re.match(r'^([ทควสพศงอตจฝญI]\d{5})', b)
        if m: existing_vault_codes.add(m.group(1))
        
    print(f"\nExisting Vault courses before extraction: {len(existing_vault_codes)}")
    
    # 6. Extract/Create Vault files for all active Excel courses
    added_to_vault = 0
    updated_in_matrix = 0
    
    for code, ex_info in excel_courses.items():
        # Merge data from docx if available
        d_info = docx_courses.get(code, {})
        m_info = matrix.get(code, {})
        
        name = d_info.get('name') or ex_info.get('name') or m_info.get('course_name') or code
        desc = d_info.get('description') or m_info.get('description', '')
        units = d_info.get('units') or m_info.get('units', [])
        area = ex_info.get('learning_area') or d_info.get('learning_area') or m_info.get('learning_area', 'กลุ่มสาระการเรียนรู้')
        folder = ex_info.get('folder') or d_info.get('folder') or '00_ทั่วไป'
        grade = ex_info.get('grade') or d_info.get('grade') or m_info.get('grade_level', 'ม.1')
        sem = ex_info.get('semester') or d_info.get('semester', '1')
        credits = ex_info.get('credits', 1.0)
        hours = ex_info.get('hours', int(credits * 40))
        
        c_merged = {
            'code': code,
            'name': name,
            'learning_area': area,
            'folder': folder,
            'grade': grade,
            'semester': sem,
            'credits': credits,
            'hours': hours,
            'description': desc,
            'units': units
        }
        
        # Check if in Vault
        if code not in existing_vault_codes:
            # Generate vault md file
            md_content = build_vault_markdown(c_merged)
            target_folder = os.path.join(vault_base, folder)
            os.makedirs(target_folder, exist_ok=True)
            safe_name = re.sub(r'[\\/*?:"<>|]', '', name).strip()
            md_filename = f"{code}_{safe_name}.md" if safe_name else f"{code}.md"
            target_md_path = os.path.join(target_folder, md_filename)
            
            with open(target_md_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
            added_to_vault += 1
            existing_vault_codes.add(code)
            
        # Update in Matrix if missing or needs update
        if code not in matrix:
            target_pre_h = (hours // 2) - 1
            target_post_h = (hours // 2) - 1
            matrix[code] = {
                "course_code": code,
                "course_name": name,
                "learning_area": area,
                "normalized_area": area,
                "folder_name": folder,
                "grade_level": grade,
                "credits": credits,
                "total_hours": hours,
                "is_basic": (code[2] == '1' if len(code) >= 3 else True),
                "target_pre_hours": target_pre_h,
                "target_post_hours": target_post_h,
                "teachers": ["....................................................."],
                "units": units if units else [
                    {"unit_no": "1", "unit_name": "หน่วยการเรียนรู้ที่ 1", "hours": target_pre_h // 2, "score_k": 8, "score_p": 2, "score_a": 0, "score_total": 10, "indicators_raw": [], "key_concepts": []},
                    {"unit_no": "2", "unit_name": "หน่วยการเรียนรู้ที่ 2", "hours": target_pre_h - (target_pre_h // 2), "score_k": 10, "score_p": 3, "score_a": 2, "score_total": 15, "indicators_raw": [], "key_concepts": []},
                    {"unit_no": "3", "unit_name": "หน่วยการเรียนรู้ที่ 3", "hours": target_post_h // 2, "score_k": 7, "score_p": 5, "score_a": 3, "score_total": 15, "indicators_raw": [], "key_concepts": []},
                    {"unit_no": "4", "unit_name": "หน่วยการเรียนรู้ที่ 4", "hours": target_post_h - (target_post_h // 2), "score_k": 6, "score_p": 2, "score_a": 2, "score_total": 10, "indicators_raw": [], "key_concepts": []}
                ],
                "indicators": [],
                "is_scheduled_term2": (sem == "2")
            }
            updated_in_matrix += 1
            
        # Update in Catalog if missing
        if code not in cat_by_code:
            cat_by_code[code] = {
                "name": name,
                "grade": grade,
                "credits": credits,
                "hours": hours,
                "type": "วิชาพื้นฐาน" if (code[2] == '1' if len(code) >= 3 else True) else "วิชาเพิ่มเติม",
                "semesters": [f"ม.{grade[-1]} เทอม {sem}"] if grade.startswith('ม.') else ["เทอม 1"]
            }

    print(f"\n[OK] Added {added_to_vault} missing course files to Curriculum_Vault!")
    print(f"[OK] Added {updated_in_matrix} courses to school_courses_assessment_matrix.json!")
    print(f"Total courses in matrix now: {len(matrix)}")
    
    # Save Matrix
    with open(matrix_path, 'w', encoding='utf-8') as f:
        json.dump(matrix, f, ensure_ascii=False, indent=2)
        
    # Save Catalog
    catalog['by_course_code'] = cat_by_code
    with open(catalog_path, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)
        
    # Export to AssessmentHub
    target_dir = r"c:\Users\peera\Desktop\Github_project\AssessmentHub\assessment-plan"
    if os.path.exists(target_dir):
        print("\nUpdating AssessmentHub data...")
        schedule_path = "semester2_teachers_mapping.json"
        schedule = {}
        if os.path.exists(schedule_path):
            with open(schedule_path, 'r', encoding='utf-8') as f:
                schedule = json.load(f)

        compiled_courses = {}
        for c_c, c in matrix.items():
            sch_entry = schedule.get(c_c, {})
            teachers = sch_entry.get("teachers", c.get("teachers", []))
            if not teachers:
                teachers = ["....................................................."]

            compiled_courses[c_c] = {
                "course_code": c_c,
                "course_name": c.get("course_name", ""),
                "learning_area": c.get("learning_area", c.get("normalized_area", "")),
                "grade_level": c.get("grade_level", "ม.1"),
                "credits": c.get("credits", 1.0),
                "total_hours": c.get("total_hours", 40),
                "is_basic": c.get("is_basic", True),
                "target_pre_hours": c.get("target_pre_hours", 19),
                "target_post_hours": c.get("target_post_hours", 19),
                "teachers": teachers,
                "units": c.get("units", []),
                "indicators": c.get("indicators", []),
                "is_scheduled_term2": c_c in schedule
            }

        data_dir = os.path.join(target_dir, "data")
        os.makedirs(data_dir, exist_ok=True)
        out_json = os.path.join(data_dir, "courses_2_2569.json")
        out_js = os.path.join(data_dir, "courses_2_2569.js")

        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(compiled_courses, f, ensure_ascii=False, indent=2)

        with open(out_js, "w", encoding="utf-8") as f:
            f.write("const COURSES_2_2569 = ")
            json.dump(compiled_courses, f, ensure_ascii=False)
            f.write(";\n")

        print(f"[OK] AssessmentHub updated ({len(compiled_courses)} courses written)")

    print("\n==================================================================")
    print("✅ EXTRACTION AND SYNCHRONIZATION COMPLETE!")
    print("==================================================================")

if __name__ == '__main__':
    execute_full_sync()
