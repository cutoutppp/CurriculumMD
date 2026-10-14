import os
import glob
import re
import json
import docx
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("==================================================================")
print("🚀 STARTING COMPLETE REBUILD OF CURRICULUM & ASSESSMENT DATABASE")
print("==================================================================")

# ==============================================================================
# PHASE 1: REBUILD all_kpi_master.json FROM CURRICULUM_VAULT
# ==============================================================================
print("\n--- PHASE 1: Rebuilding all_kpi_master.json (2,056 Core KPIs) ---")

SUBJECT_NAMES = {
    '01': 'ภาษาไทย',
    '02': 'คณิตศาสตร์',
    '03': 'วิทยาศาสตร์และเทคโนโลยี',
    '04': 'สังคมศึกษา ศาสนา และวัฒนธรรม',
    '05': 'สุขศึกษาและพลศึกษา',
    '06': 'ศิลปะ',
    '07': 'การงานอาชีพ',
    '08': 'ภาษาต่างประเทศ'
}

def clean_wikilinks(text):
    if not text:
        return ""
    text = re.sub(r'\[\[[^\]|]+\|([^\]]+)\]\]', r'\1', text)
    text = re.sub(r'\[\[([^\]]+)\]\]', r'\1', text)
    return text.strip()

master_kpis = {}
kpi_types_dict = {}

for i in range(1, 9):
    key = f"0{i}"
    subj_name = SUBJECT_NAMES[key]
    f_list = glob.glob(f'Curriculum_Vault/{key}*/**/*.md', recursive=True)
    
    for f in f_list:
        if os.path.basename(f).startswith('00_'):
            continue
            
        with open(f, 'r', encoding='utf-8') as fp:
            txt = fp.read()
            
        m_code = re.search(r'code:\s*"([^"]+)"', txt)
        if not m_code:
            m_code = re.search(r'^#\s+([ทควสพศงต]\s*\d+\.\d+\s+[ปม]\.[\d\/\-]+)', txt, re.MULTILINE)
            
        if not m_code:
            continue
            
        raw_code = m_code.group(1).strip()
        code = re.sub(r'\s+', ' ', raw_code)
        # Normalize code format e.g. "ท 1.1 ป.1/1"
        code = re.sub(r'([ทควสพศงต])\s*\.?\s*(\d+\.\d+)\s*([ปม]\.[\d\/\-]+)', r'\1 \2 \3', code)
        
        m_type = re.search(r'indicator_type:\s*(.+)', txt)
        ind_type = m_type.group(1).strip() if m_type else "ระหว่างทาง"
        if "ปลายทาง" in ind_type:
            ind_type = "ปลายทาง"
        else:
            ind_type = "ระหว่างทาง"
            
        m_grade = re.search(r'grade:\s*(.+)', txt)
        grade = m_grade.group(1).strip() if m_grade else ""
        
        m_std = re.search(r'มาตรฐาน:\s*(?:\[\[[^\]]+\|)?(?:มาตรฐาน\s*)?([ทควสพศงต]\s*\d+\.\d+)', txt)
        standard = m_std.group(1).strip() if m_std else ""
        if not standard:
            m_std2 = re.search(r'([ทควสพศงต]\s*\d+\.\d+)', code)
            standard = m_std2.group(1).strip() if m_std2 else ""
            
        m_strand = re.search(r'strand:\s*"([^"]+)"', txt)
        if not m_strand:
            m_strand = re.search(r'สาระ:\s*(?:\[\[[^\]]+\|)?(?:สาระที่\s*\d+\s*)?([^)\n]+)', txt)
        strand = m_strand.group(1).strip() if m_strand else ""
        strand = clean_wikilinks(strand).replace('(', '').replace(')', '').strip()
        
        lines = txt.splitlines()
        quote_lines = []
        is_quote = False
        for line in lines:
            if line.startswith('>'):
                quote_lines.append(line.lstrip('>').strip())
                is_quote = True
            elif is_quote and line.strip() and not line.startswith('**') and not line.startswith('#'):
                quote_lines.append(line.strip())
            elif is_quote and (not line.strip() or line.startswith('**') or line.startswith('#')):
                break
                
        kpi_text = clean_wikilinks(" ".join(quote_lines)).strip()
        kpi_text = re.sub(r'\s+', ' ', kpi_text)
        
        core_content = ""
        parts = txt.split('**สาระการเรียนรู้แกนกลาง:**')
        if len(parts) > 1:
            raw_core = parts[1].strip()
            next_sec = re.split(r'\n(?=##|---|#|\*\*)', raw_core)
            core_content = clean_wikilinks(next_sec[0]).strip()
            core_content = re.sub(r'\n+', '\n', core_content)
            
        master_kpis[code] = {
            "code": code,
            "text": kpi_text,
            "type": ind_type,
            "subject": subj_name,
            "grade": grade,
            "standard": standard,
            "strand": strand,
            "core_content": core_content
        }
        kpi_types_dict[code] = ind_type

print(f"✅ Rebuilt master KPIs: {len(master_kpis)} entries (with full text and core_content)")

with open('all_kpi_master.json', 'w', encoding='utf-8') as fp:
    json.dump(master_kpis, fp, ensure_ascii=False, indent=2)

with open('all_kpi_types.json', 'w', encoding='utf-8') as fp:
    json.dump(kpi_types_dict, fp, ensure_ascii=False, indent=2)

print("✅ Saved all_kpi_master.json & all_kpi_types.json successfully!")

# ==============================================================================
# PHASE 2: EXTRACT LEARNING OUTCOMES FOR ELECTIVE COURSES
# ==============================================================================
print("\n--- PHASE 2: Extracting Learning Outcomes for Elective Courses ---")

course_outcomes = {}

# 1. From Docx files in school_curriculum_raw
docx_files = glob.glob('school_curriculum_raw/**/*.docx', recursive=True)
for f in docx_files:
    try:
        doc = docx.Document(f)
    except:
        continue
    full_text = "\n".join([p.text for p in doc.paragraphs])
    course_blocks = re.split(r'(?:รหัส(?:วิชา)?\s*([ก-ฮA-Za-z]\s*\d{5}))', full_text)
    if len(course_blocks) > 1:
        for idx in range(1, len(course_blocks), 2):
            raw_code = course_blocks[idx]
            block = course_blocks[idx+1]
            code = re.sub(r'\s+', '', raw_code)
            
            m_lo = re.search(r'ผลการเรียนรู้\s*\n(.*?)(?=\n\s*(?:โครงสร้างรายวิชา|คำอธิบายรายวิชา|รหัสวิชา|\Z))', block, re.DOTALL)
            if m_lo:
                lo_text = m_lo.group(1).strip()
                # If all combined e.g. "1. ... 2. ... 3. ..."
                split_items = re.split(r'(?:^|\s+)(?=\d+[\.\)]\s*)', lo_text)
                clean_items = []
                for it in split_items:
                    c_it = re.sub(r'^\d+[\.\)]\s*', '', it).strip()
                    c_it = re.sub(r'\s+', ' ', c_it)
                    if len(c_it) > 5 and not c_it.startswith('รวมทั้ง'):
                        clean_items.append(c_it)
                if clean_items and (code not in course_outcomes or len(clean_items) > len(course_outcomes[code])):
                    course_outcomes[code] = clean_items

# 2. From Curriculum_Vault/09_หลักสูตรสถานศึกษา
vault_school_files = glob.glob('Curriculum_Vault/09_หลักสูตรสถานศึกษา/**/*.md', recursive=True)
for vf in vault_school_files:
    fname = os.path.basename(vf)
    m_code = re.match(r'([ก-ฮA-Za-z]\d{5})', fname)
    if not m_code:
        continue
    code = m_code.group(1)
    with open(vf, 'r', encoding='utf-8') as fp:
        vtxt = fp.read()
    
    # Check if there is an explicit outcome list in description or text
    m_lo = re.search(r'ผลการเรียนรู้\s*\n(.*?)(?=\n\s*(?:##|---|🎯|\Z))', vtxt, re.DOTALL)
    if m_lo:
        lo_text = m_lo.group(1).strip()
        split_items = re.split(r'(?:^|\s+)(?=\d+[\.\)]\s*)', lo_text)
        clean_items = []
        for it in split_items:
            c_it = re.sub(r'^\d+[\.\)]\s*', '', it).strip()
            c_it = re.sub(r'\s+', ' ', c_it)
            if len(c_it) > 5 and not c_it.startswith('รวมทั้ง'):
                clean_items.append(c_it)
        if clean_items and (code not in course_outcomes or len(clean_items) > len(course_outcomes[code])):
            course_outcomes[code] = clean_items

print(f"✅ Extracted learning outcome dictionaries for {len(course_outcomes)} courses!")

# ==============================================================================
# PHASE 3: PROCESS & CLEAN ALL 583 COURSES
# ==============================================================================
print("\n--- PHASE 3: Cleaning & Linking School Courses Assessment Matrix ---")

# Load existing matrix and schedule
with open('school_courses_assessment_matrix.json', 'r', encoding='utf-8') as fp:
    matrix = json.load(fp)

with open('semester2_teachers_mapping.json', 'r', encoding='utf-8') as fp:
    schedule = json.load(fp)

# Area normalization map
PREFIX_AREA_MAP = {
    'ท': 'ภาษาไทย',
    'ค': 'คณิตศาสตร์',
    'ว': 'วิทยาศาสตร์และเทคโนโลยี',
    'ส': 'สังคมศึกษา ศาสนา และวัฒนธรรม',
    'พ': 'สุขศึกษาและพลศึกษา',
    'ศ': 'ศิลปะ',
    'ง': 'การงานอาชีพ',
    'อ': 'ภาษาต่างประเทศ',
    'จ': 'ภาษาต่างประเทศ',
    'ฝ': 'ภาษาต่างประเทศ',
    'ญ': 'ภาษาต่างประเทศ',
    'I': 'กิจกรรมพัฒนาผู้เรียน'
}

AREA_TO_FOLDER = {
    'ภาษาไทย': '01_ภาษาไทย',
    'คณิตศาสตร์': '02_คณิตศาสตร์',
    'วิทยาศาสตร์และเทคโนโลยี': '03_วิทยาศาสตร์และเทคโนโลยี',
    'สังคมศึกษา ศาสนา และวัฒนธรรม': '04_สังคมศึกษา',
    'สุขศึกษาและพลศึกษา': '05_สุขศึกษาและพลศึกษา',
    'ศิลปะ': '06_ศิลปะ',
    'การงานอาชีพ': '07_การงานอาชีพ',
    'ภาษาต่างประเทศ': '08_ภาษาต่างประเทศ'
}

def normalize_area_name(area, code):
    if not area or len(area) > 35 or 'และ ประสบการณ์' in area:
        first = code[0] if code else ''
        return PREFIX_AREA_MAP.get(first, 'กลุ่มสาระการเรียนรู้')
    area = area.replace('สุขศีกษา', 'สุขศึกษา')
    area = area.replace('วิทยาศาสตร์ และเทคโนโลยีและเทคโนโลยี', 'วิทยาศาสตร์และเทคโนโลยี')
    area = area.replace('วิทยาศาสตร์ และเทคโนโลยี', 'วิทยาศาสตร์และเทคโนโลยี')
    area = area.replace('ภาษาต่างประเทศ (ภาษาอังกฤษ)', 'ภาษาต่างประเทศ')
    return area.strip()

master_codes = set(master_kpis.keys())

def extract_clean_basic_kpis(text, course_code):
    """
    Intelligently extracts valid KPI codes from raw text:
    e.g. 'ง 2.1 เข้าใจ... ตัวชี้วัดระหว่างทาง ม.1/2 ระบุ...' -> ['ง 2.1 ม.1/2']
    """
    found = []
    text = text.replace('\n', ' ').replace('\t', ' ')
    
    # 1. Wikilinks [[...]]
    links = re.findall(r'\[\[(?:[^\]|]+\|)?([ทควสพศงต]\s*\d+\.\d+\s*[ปม]\.[\d\/\-]+)\]\]', text)
    for l in links:
        norm = re.sub(r'\s+', ' ', l).strip()
        norm = re.sub(r'([ทควสพศงต])\s*(\d+\.\d+)\s*([ปม]\.[\d\/\-]+)', r'\1 \2 \3', norm)
        if norm in master_codes:
            found.append(norm)

    # 2. Direct standard + indicator code match
    # e.g. "ว 2.1 ม.1/1", "ท 1.1 ม 1/1", "ส 4.2 ม 4-6/3", "พ 3.1 ม.1/1-2"
    direct = re.findall(r'([ทควสพศงต])\s*(\d+\.\d+)\s*(?:ตัวชี้ว(?:ัด|ตัด)(?:ระหว่างทาง|ปลายทาง)?\s*)?([ปม]\s*\.?\s*[\d\-\/]+)', text)
    for subj, std_num, grade_ind in direct:
        clean_gi = re.sub(r'\s+', '', grade_ind)
        if not clean_gi.startswith('ม.') and not clean_gi.startswith('ป.'):
            clean_gi = clean_gi[0] + '.' + clean_gi[1:]
        
        m_range = re.match(r'([ปม]\.(?:\d+|\d+-\d+))\/(\d+)\-(\d+)', clean_gi)
        if m_range:
            g_prefix, start_n, end_n = m_range.group(1), int(m_range.group(2)), int(m_range.group(3))
            for n in range(start_n, end_n + 1):
                c_code = f"{subj} {std_num} {g_prefix}/{n}"
                if c_code in master_codes:
                    found.append(c_code)
        else:
            full = f"{subj} {std_num} {clean_gi}"
            if full in master_codes:
                found.append(full)
                
    # 3. Contextual standard + indicator match
    std_matches = list(re.finditer(r'([ทควสพศงต])\s*(\d+\.\d+)', text))
    if std_matches:
        for idx, sm in enumerate(std_matches):
            subj = sm.group(1)
            std_num = sm.group(2)
            std_str = f"{subj} {std_num}"
            
            start_pos = sm.start()
            end_pos = std_matches[idx+1].start() if idx+1 < len(std_matches) else len(text)
            chunk = text[start_pos:end_pos]
            
            ind_matches = re.findall(r'([ปม]\s*\.?\s*[\d\-]+(?:\s*\/\s*\d+(?:\s*-\s*\d+)?)?)', chunk)
            for im in ind_matches:
                clean_im = re.sub(r'\s+', '', im)
                if not clean_im.startswith('ม.') and not clean_im.startswith('ป.'):
                    clean_im = clean_im[0] + '.' + clean_im[1:]
                m_range = re.match(r'([ปม]\.(?:\d+|\d+-\d+))\/(\d+)\-(\d+)', clean_im)
                if m_range:
                    g_prefix, start_n, end_n = m_range.group(1), int(m_range.group(2)), int(m_range.group(3))
                    for n in range(start_n, end_n + 1):
                        c_code = f"{std_str} {g_prefix}/{n}"
                        if c_code in master_codes:
                            found.append(c_code)
                else:
                    c_code = f"{std_str} {clean_im}"
                    if c_code in master_codes:
                        found.append(c_code)

    return list(dict.fromkeys(found))

def parse_course_markdown(fpath):
    with open(fpath, 'r', encoding='utf-8') as fp:
        content = fp.read()
        
    m_code = re.search(r'รหัสวิชา:\s*"?([^\n"]+)"?', content)
    m_name = re.search(r'ชื่อรายวิชา:\s*"?([^\n"]+)"?', content)
    m_area = re.search(r'กลุ่มสาระ:\s*"?([^\n"]+)"?', content)
    m_grade = re.search(r'ระดับชั้น:\s*"?([^\n"]+)"?', content)
    m_cred = re.search(r'หน่วยกิต:\s*([\d\.]+)', content)
    m_hrs = re.search(r'เวลาเรียน:\s*(\d+)', content)
    
    code = m_code.group(1).strip() if m_code else ""
    name = m_name.group(1).strip() if m_name else ""
    area = m_area.group(1).strip() if m_area else PREFIX_AREA_MAP.get(code[0] if code else '', '')
    grade = m_grade.group(1).strip() if m_grade else "ม.1"
    credits = float(m_cred.group(1)) if m_cred else 1.0
    total_hours = int(m_hrs.group(1)) if m_hrs else int(credits * 40)
    
    clean_code = re.sub(r'\s+', '', code)
    m_type = re.match(r'^[ก-๙a-zA-Z]+(\d)(\d)(\d)', clean_code)
    is_basic = (m_type and m_type.group(3) == '1') or bool(re.match(r'^[ก-๙a-zA-Z]+\d01', clean_code))
    target_pre_h = (total_hours // 2) - 1
    target_post_h = (total_hours // 2) - 1
    
    units = []
    course_indicators = []
    table_lines = [l for l in content.splitlines() if l.startswith('|') and not l.startswith('| :') and not l.startswith('| หน่วยที่')]
    
    for line in table_lines:
        orig_cols = [c.strip() for c in line.split('|')[1:-1]]
        c_line = re.sub(r'\[\[[^\]|]+\|([^\]]+)\]\]', r'\1', line)
        c_line = re.sub(r'\[\[([^\]]+)\]\]', r'\1', c_line)
        cols = [c.strip() for c in c_line.split('|')[1:-1]]
        if len(cols) < 5:
            continue
        u_no_raw = cols[0]
        u_no_clean = re.sub(r'[\.\s]', '', u_no_raw)
        if not u_no_clean.isdigit():
            continue
            
        u_no = u_no_clean
        u_name = re.sub(r'^\*+|\*+$', '', cols[1]).strip()
        raw_ind_text = cols[2].replace('<br>', '\n')
        orig_ind_text = orig_cols[2] if len(orig_cols) > 2 else ""
        
        concepts = cols[3] if len(cols) > 3 else ""
        try:
            u_h = int(re.sub(r'[^\d]', '', cols[4]))
        except:
            u_h = 0
            
        sk, sp, sa, stot = 0, 0, 0, 0
        if len(cols) >= 9:
            try: sk = int(re.sub(r'[^\d]', '', cols[5]))
            except: pass
            try: sp = int(re.sub(r'[^\d]', '', cols[6]))
            except: pass
            try: sa = int(re.sub(r'[^\d]', '', cols[7]))
            except: pass
            try: stot = int(re.sub(r'\*+', '', cols[8]))
            except: stot = sk + sp + sa

        if u_h == 0 and len(cols) >= 9:
            try:
                candidate_h = int(re.sub(r'[^\d]', '', cols[5]))
                candidate_k = int(re.sub(r'[^\d]', '', cols[6]))
                candidate_p = int(re.sub(r'[^\d]', '', cols[7]))
                candidate_tot = int(re.sub(r'\*+', '', cols[8]))
                if candidate_h > 0 and candidate_tot > 0:
                    u_h = candidate_h
                    sk = candidate_k
                    sp = candidate_p
                    sa = max(0, candidate_tot - (sk + sp))
                    stot = candidate_tot
            except:
                pass
            
        unit_kpi_codes = []
        unit_indicators = []
        
        # 1. First, extract wikilinks from orig_ind_text
        wikilinks = re.findall(r'\[\[(?:[^\]|]+\|)?([ทควสพศงต]\s*\d+\.\d+\s*[ปม]\.[\d\/\-]+)\]\]', orig_ind_text)
        for wl in wikilinks:
            norm_wl = re.sub(r'\s+', ' ', wl).strip()
            norm_wl = re.sub(r'([ทควสพศงต])\s*(\d+\.\d+)\s*([ปม]\.[\d\/\-]+)', r'\1 \2 \3', norm_wl)
            if norm_wl in master_codes and norm_wl not in unit_kpi_codes:
                unit_kpi_codes.append(norm_wl)

        clean_raw_text = re.split(r'🔹\s*ตัวชี้วัด\s*สพฐ\.:', raw_ind_text)[0]

        if is_basic:
            # 2. Extract from raw text
            text_kpis = extract_clean_basic_kpis(clean_raw_text, code)
            for kcode in text_kpis:
                if kcode not in unit_kpi_codes:
                    unit_kpi_codes.append(kcode)

            for kcode in unit_kpi_codes:
                kmeta = master_kpis.get(kcode, {})
                ktype = kmeta.get('type', '')
                ktext = kmeta.get('text', '')
                type_tag = f" ({ktype})" if ktype else ""
                full_line = f"{kcode}{type_tag}: {ktext}" if ktext else kcode
                unit_indicators.append(full_line)
                if full_line not in course_indicators:
                    course_indicators.append(full_line)
            if not unit_indicators:
                clean_raw = re.sub(r'\s+', ' ', clean_raw_text).strip()
                unit_indicators = [clean_raw] if clean_raw else [f"ตัวชี้วัดตามหลักสูตรแกนกลาง หน่วยที่ {u_no}"]
                if clean_raw and clean_raw not in course_indicators:
                    course_indicators.append(clean_raw)
        else:
            lines = [l.strip() for l in clean_raw_text.split('\n') if l.strip()]
            for l in lines:
                l_clean = re.sub(r'\s+', ' ', l).strip()
                if l_clean and len(l_clean) > 2 and not l_clean.startswith('สาระ') and not l_clean.startswith('🔹'):
                    unit_indicators.append(l_clean)
                    if l_clean not in course_indicators:
                        course_indicators.append(l_clean)
            if not unit_indicators:
                unit_indicators = [f"ผลการเรียนรู้ที่ {u_no}"]
                if f"ผลการเรียนรู้ที่ {u_no}" not in course_indicators:
                    course_indicators.append(f"ผลการเรียนรู้ที่ {u_no}")
                    
        existing_unit = next((u for u in units if u["unit_no"] == u_no), None)
        if existing_unit:
            if existing_unit["hours"] == 0 and u_h > 0:
                existing_unit["hours"] = u_h
            existing_unit["score_k"] += sk
            existing_unit["score_p"] += sp
            existing_unit["score_a"] += sa
            existing_unit["score_total"] += stot
            for ind in unit_indicators:
                if ind not in existing_unit["indicators"]:
                    existing_unit["indicators"].append(ind)
                    existing_unit["kpis"].append(ind)
            for kcode in unit_kpi_codes:
                if kcode not in existing_unit["national_kpis"]:
                    existing_unit["national_kpis"].append(kcode)
            if concepts and concepts not in existing_unit["concepts"]:
                existing_unit["concepts"].append(concepts)
        else:
            units.append({
                "unit_no": u_no,
                "unit_name": u_name,
                "hours": u_h,
                "score_k": sk,
                "score_p": sp,
                "score_a": sa,
                "score_total": stot,
                "national_kpis": unit_kpi_codes,
                "kpis": unit_indicators,
                "indicators": unit_indicators,
                "concepts": [concepts] if concepts else []
            })

    folder_name = AREA_TO_FOLDER.get(area, "")
    if not folder_name:
        folder_name = AREA_TO_FOLDER.get(PREFIX_AREA_MAP.get(code[0] if code else '', ''), "")

    return {
        "course_code": code,
        "course_name": name,
        "learning_area": area,
        "normalized_area": area,
        "folder_name": folder_name,
        "grade_level": grade,
        "credits": credits,
        "total_hours": total_hours,
        "is_basic": is_basic,
        "target_pre_hours": target_pre_h,
        "target_post_hours": target_post_h,
        "units": units,
        "indicators": course_indicators
    }

vault_school_files = glob.glob('Curriculum_Vault/09_หลักสูตรสถานศึกษา/**/*.md', recursive=True)
vault_map = {}
for vf in vault_school_files:
    fname = os.path.basename(vf)
    m = re.match(r'([ก-ฮA-Za-z]\d{5})', fname)
    if m:
        vault_map[m.group(1)] = vf

clean_matrix = {}
stats = {'basic': 0, 'elective': 0, 'basic_linked': 0, 'elective_enriched': 0}

all_course_codes = sorted(list(set(matrix.keys()) | set(vault_map.keys())))

for code in all_course_codes:
    c_raw = matrix.get(code, {})
    vf = vault_map.get(code)
    
    if vf:
        parsed = parse_course_markdown(vf)
        name = parsed["course_name"] or c_raw.get("course_name", "")
        area = normalize_area_name(parsed["learning_area"] or c_raw.get("learning_area"), code)
        grade = parsed["grade_level"] or c_raw.get("grade_level", "ม.1")
        credits = parsed["credits"] or c_raw.get("credits", 1.0)
        total_hours = parsed["total_hours"] or c_raw.get("total_hours", 40)
        is_basic = parsed["is_basic"]
        target_pre_h = parsed["target_pre_hours"]
        target_post_h = parsed["target_post_hours"]
        units = parsed["units"]
        indicators = parsed["indicators"]
        if code == "ท20210" and not units:
            th = target_pre_h
            h1, h2 = th // 2, th - (th // 2)
            indicators = [
                "1. อ่านและเขียนคำที่ใช้อักษรนำและคำควบกล้ำได้ถูกต้อง",
                "2. อ่านและเขียนคำสมาส คำสนธิ และคำที่มาจากภาษาต่างประเทศได้ถูกต้อง",
                "3. อ่านและเขียนคำที่มี ร หัน (รร) และคำที่มี ฤ ได้ถูกต้อง",
                "4. ใช้คำไทยและคำพ้องรูป พ้องเสียง ได้ถูกต้องตามบริบท"
            ]
            units = [
                {"unit_no": "1", "unit_name": "หลักการอ่านคำไทย", "hours": h1, "score_k": 10, "score_p": 5, "score_a": 2, "score_total": 17, "indicators": indicators[:1], "kpis": indicators[:1], "national_kpis": [], "concepts": []},
                {"unit_no": "2", "unit_name": "หลักการเขียนสะกดคำไทย", "hours": h2, "score_k": 10, "score_p": 6, "score_a": 2, "score_total": 18, "indicators": indicators[1:2], "kpis": indicators[1:2], "national_kpis": [], "concepts": []},
                {"unit_no": "3", "unit_name": "การอ่านและเขียนคำราชาศัพท์และคำยืมภาษาต่างประเทศ", "hours": h1, "score_k": 10, "score_p": 5, "score_a": 2, "score_total": 17, "indicators": indicators[2:3], "kpis": indicators[2:3], "national_kpis": [], "concepts": []},
                {"unit_no": "4", "unit_name": "การประยุกต์ใช้การอ่านและเขียนคำไทยในชีวิตประจำวัน", "hours": h2, "score_k": 10, "score_p": 6, "score_a": 2, "score_total": 18, "indicators": indicators[3:4], "kpis": indicators[3:4], "national_kpis": [], "concepts": []},
            ]
    else:
        name = c_raw.get("course_name", "")
        area = normalize_area_name(c_raw.get("learning_area"), code)
        grade = c_raw.get("grade_level", "ม.1")
        clean_code = re.sub(r'\s+', '', code)
        m_type = re.match(r'^[ก-๙a-zA-Z]+(\d)(\d)(\d)', clean_code)
        is_basic = (m_type and m_type.group(3) == '1') or bool(re.match(r'^[ก-๙a-zA-Z]+\d01', clean_code))
        target_pre_h = (total_hours // 2) - 1
        target_post_h = (total_hours // 2) - 1
        units = c_raw.get("units", [])
        indicators = c_raw.get("indicators", [])

    if is_basic:
        stats['basic'] += 1
        if any(u.get("national_kpis") for u in units):
            stats['basic_linked'] += 1
    else:
        stats['elective'] += 1

    # Enrich elective outcomes if unit has placeholder
    known_outcomes = course_outcomes.get(code, [])
    if not is_basic and known_outcomes:
        enriched_indicators = []
        for u in units:
            u_inds = []
            for ind in u.get("indicators", []):
                m_num = re.search(r'(?:ผลการเรียนรู้\s*(?:ข้อ)?\s*ที่\s*|ข้อที่\s*)(\d+)', ind)
                if m_num:
                    n = int(m_num.group(1))
                    if 1 <= n <= len(known_outcomes):
                        clean_lo = f"ผลการเรียนรู้ที่ {n}: {known_outcomes[n-1]}"
                        u_inds.append(clean_lo)
                        if clean_lo not in enriched_indicators:
                            enriched_indicators.append(clean_lo)
                        continue
                u_inds.append(ind)
                if ind not in enriched_indicators:
                    enriched_indicators.append(ind)
            u["indicators"] = u_inds
            u["kpis"] = u_inds
        if enriched_indicators:
            indicators = enriched_indicators
            stats['elective_enriched'] += 1

    # Filter out fake strand indicators from course indicators
    clean_course_inds = []
    seen_kpi_codes = set()
    for ind in indicators:
        if ind.startswith('สาระ') or ind.startswith('กลุ่มสาระ'):
            continue
        m_code = re.match(r'([ทควสพศงต]\s*\d+\.\d+\s*[ปม]\.[\d\/\-]+)', ind)
        if m_code:
            k = m_code.group(1).replace(' ', '')
            if k in seen_kpi_codes:
                continue
            seen_kpi_codes.add(k)
        if ind not in clean_course_inds:
            clean_course_inds.append(ind)

    # Teachers from schedule
    sch_entry = schedule.get(code, {})
    teachers = sch_entry.get("teachers", [])
    if not teachers:
        teachers = ["....................................................."]

    folder_name = AREA_TO_FOLDER.get(area, "")
    if not folder_name:
        folder_name = AREA_TO_FOLDER.get(PREFIX_AREA_MAP.get(code[0] if code else '', ''), "")

    clean_matrix[code] = {
        "course_code": code,
        "course_name": name,
        "learning_area": area,
        "normalized_area": area,
        "folder_name": folder_name,
        "grade_level": grade,
        "credits": credits,
        "total_hours": total_hours,
        "is_basic": is_basic,
        "target_pre_hours": target_pre_h,
        "target_post_hours": target_post_h,
        "teachers": teachers,
        "units": units,
        "indicators": clean_course_inds,
        "is_scheduled_term2": code in schedule
    }

print(f"✅ Cleaned matrix: {len(clean_matrix)} courses processed.")
print(f"   - Basic courses: {stats['basic']} (Linked units: {stats['basic_linked']})")
print(f"   - Elective courses: {stats['elective']} (Enriched units: {stats['elective_enriched']})")

with open('school_courses_assessment_matrix.json', 'w', encoding='utf-8') as fp:
    json.dump(clean_matrix, fp, ensure_ascii=False, indent=2)

print("✅ Saved school_courses_assessment_matrix.json successfully!")

# ==============================================================================
# PHASE 4: EXPORT TO ASSESSMENTHUB (Web App)
# ==============================================================================
print("\n--- PHASE 4: Exporting to AssessmentHub (courses_2_2569.json & .js) ---")

web_dest_dir = r"c:\Users\peera\Desktop\Github_project\AssessmentHub\assessment-plan\data"
os.makedirs(web_dest_dir, exist_ok=True)

# Also load existing school teachers mapping
teachers_by_area = {}
with open(os.path.join(web_dest_dir, "courses_2_2569.js"), "r", encoding="utf-8") as fp:
    js_content = fp.read()
    m_tea = re.search(r'window\.SCHOOL_TEACHERS_BY_AREA\s*=\s*(\{.*?\});', js_content, re.DOTALL)
    if m_tea:
        try:
            teachers_by_area = json.loads(m_tea.group(1))
        except:
            pass

# Save courses_2_2569.json
json_dest = os.path.join(web_dest_dir, "courses_2_2569.json")
with open(json_dest, "w", encoding="utf-8") as fp:
    json.dump(clean_matrix, fp, ensure_ascii=False, indent=2)

# Save courses_2_2569.js (with window.COURSES_DATA & window.SCHOOL_TEACHERS_BY_AREA)
js_dest = os.path.join(web_dest_dir, "courses_2_2569.js")
with open(js_dest, "w", encoding="utf-8") as fp:
    fp.write("// Auto-generated & Normalized Course & Teacher Data for Term 2/2569\n")
    fp.write("window.COURSES_DATA = ")
    json.dump(clean_matrix, fp, ensure_ascii=False, indent=2)
    fp.write(";\n\n")
    if teachers_by_area:
        fp.write("window.SCHOOL_TEACHERS_BY_AREA = ")
        json.dump(teachers_by_area, fp, ensure_ascii=False, indent=2)
        fp.write(";\n")

print(f"✅ Successfully exported courses_2_2569.json ({os.path.getsize(json_dest):,} bytes)")
print(f"✅ Successfully exported courses_2_2569.js ({os.path.getsize(js_dest):,} bytes)")

print("\n==================================================================")
print("🎉 REBUILD & NORMALIZATION COMPLETE!")
print("==================================================================")
