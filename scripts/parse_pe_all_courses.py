import docx
import re
import json

THAI_TO_ARABIC = str.maketrans('๐๑๒๓๔๕๖๗๘๙', '0123456789')
def clean(t):
    return t.translate(THAI_TO_ARABIC) if t else ''

def parse_pe_docs():
    p_ton = 'school_curriculum_raw/หลักสูตรกลุ่มสาระฯ 69/สุขศึกษา 69/5 ส่วนประกอบของหลักสูตร กลุ่มสาระ สุขศึกษา ม.ต้น มีน 11พ.ค.69(1).docx'
    p_plai = 'school_curriculum_raw/หลักสูตรกลุ่มสาระฯ 69/สุขศึกษา 69/5 ส่วนประกอบของหลักสูตร กลุ่มสาระ สุขศึกษาและพลศึกษา ม.ปลาย พ.ค. 2569.docx'

    courses = {}

    for path, is_ton in [(p_ton, True), (p_plai, False)]:
        doc = docx.Document(path)
        current_code = None
        current_name = None
        current_lines = []

        for p in doc.paragraphs:
            t = clean(p.text.strip())
            m_code = re.search(r'(พ\s*2[1-3]10[1-4]|พ\s*3[1-3]10[1-2])', t)
            if m_code and ('รายวิชา' in t or 'วิชา' in t or 'รหัส' in t):
                code = m_code.group(1).replace(' ', '')
                if current_code and current_lines:
                    courses.setdefault(current_code, {'name': current_name, 'lines': []})['lines'].extend(current_lines)
                current_code = code
                current_name = t
                current_lines = []
            elif current_code:
                current_lines.append(t)
        
        if current_code and current_lines:
            courses.setdefault(current_code, {'name': current_name, 'lines': []})['lines'].extend(current_lines)

    # Now parse indicators from lines of each course
    course_kpis = {}
    for code, c_data in sorted(courses.items()):
        lines = c_data['lines']
        kpis = []
        current_std = None
        for l in lines:
            if 'คำอธิบายรายวิชา' in l and code not in l:
                # possible next course header without trigger
                pass
            m_std = re.search(r'พ\s*([1-5]\.[1-2])', l)
            if m_std:
                current_std = f"พ {m_std.group(1)}"
            if current_std:
                # match indicators
                items = re.findall(r'ม\.?\s*([1-6]|4-6)\s*/\s*([0-9]+(?:\s*-\s*[0-9]+)?)', l)
                for gr, num_range in items:
                    gr_str = f"ม.{gr}" if gr != "4-6" else "ม.4-6"
                    if '-' in num_range:
                        s_n, e_n = map(int, num_range.split('-'))
                        for n in range(s_n, e_n + 1):
                            kpis.append(f"{current_std} {gr_str}/{n}")
                    else:
                        kpis.append(f"{current_std} {gr_str}/{int(num_range)}")
                nums = re.findall(r'(?:^|[,\s])([0-9]+)(?=[,\s]|$)', l)
                # handle continuation lines like ม.1/1, 2, 3
                if 'ม.' in l and not items:
                    # e.g. ม.1/1, ม.1/2
                    pass
        course_kpis[code] = sorted(list(dict.fromkeys(kpis)))

    with open('pe_parsed_results.json', 'w', encoding='utf-8') as out:
        json.dump(course_kpis, out, ensure_ascii=False, indent=2)

    print(f"Parsed {len(course_kpis)} PE courses.")
    for c, ks in sorted(course_kpis.items()):
        print(f"  {c}: {len(ks)} KPIs -> {ks[:4]} ...")

parse_pe_docs()
