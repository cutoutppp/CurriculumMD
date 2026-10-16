# -*- coding: utf-8 -*-
"""
Deep Comprehensive Audit: School Curriculum Extraction Completeness
Checks all raw files (.docx, .doc, .pdf, .xlsx) in school_curriculum_raw
against Curriculum_Vault, school_courses_assessment_matrix.json, and semester_catalog.json.
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

def run_audit():
    print("==================================================================")
    print("🏥 AUDITING SCHOOL CURRICULUM EXTRACTION STATUS (โรงเรียนพัฒนานิคม)")
    print("==================================================================")

    # 1. Base folders
    cwd = os.getcwd()
    raw_root = os.path.join(cwd, 'school_curriculum_raw')
    top_entries = os.listdir(raw_root)
    top_folder = [e for e in top_entries if os.path.isdir(os.path.join(raw_root, e))][0]
    raw_base = os.path.join(raw_root, top_folder)

    print(f"Raw Base: {raw_base}\n")

    # 2. Parse Excel Master
    excel_files = [f for f in os.listdir(raw_base) if f.endswith('.xlsx')]
    xlsx_path = os.path.join(raw_base, excel_files[0])
    print(f"Reading School Master Excel: {excel_files[0]}")
    wb = openpyxl.load_workbook(xlsx_path, data_only=True)
    
    excel_active_courses = {} # code -> dict(name, credits, sheet, grade)
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
                # Find course codes: e.g. ว21103, ค 20213, อ 20226, I20201
                matches = re.finditer(r'([ทควสพศงอตจฝญI]\s*\d{5})\s*([^\d\n\r]+)?', s)
                for m in matches:
                    c_code = re.sub(r'\s+', '', m.group(1))
                    c_name = m.group(2).strip() if m.group(2) else ""
                    # Clean trailing credits or parentheses
                    c_name = re.sub(r'\s*\d+\.\d+.*$', '', c_name).strip()
                    if c_code not in excel_active_courses or (not excel_active_courses[c_code]['name'] and c_name):
                        excel_active_courses[c_code] = {
                            'code': c_code,
                            'name': c_name,
                            'sheet': sname,
                            'raw_str': s
                        }

    print(f"Total active course codes in School Master Excel: {len(excel_active_courses)}")

    # 3. Scan all DOCX files in raw_base
    print("\nScanning all DOCX files for course specifications...")
    docx_files = []
    for root, dirs, files in os.walk(raw_base):
        for f in files:
            if f.endswith('.docx') and not f.startswith('~$'):
                docx_files.append(os.path.join(root, f))

    print(f"Total DOCX files found: {len(docx_files)}")

    courses_in_docx = {} # code -> dict(name, files, has_description, has_units, has_indicators)

    for df in docx_files:
        try:
            doc = docx.Document(df)
            full_text = []
            for p in doc.paragraphs:
                if p.text.strip():
                    full_text.append(p.text.strip())
            
            doc_str = "\n".join(full_text)
            # Normalize Thai digits to Arabic digits in text
            thai_digits = str.maketrans('๐๑๒๓๔๕๖๗๘๙', '0123456789')
            doc_str_norm = doc_str.translate(thai_digits)
            
            # Find course headers
            # Pattern 1: รหัสวิชา [code] รายวิชา [name]
            pats = [
                r'รหัสวิชา\s*([ทควสพศงอตจฝญI]\s*\d{5})\s*(?:รายวิชา\s*([^\n\t\r]+))?',
                r'รายวิชา\s*([^\n\t\r]+)\s*รหัสวิชา\s*([ทควสพศงอตจฝญI]\s*\d{5})',
                r'([ทควสพศงอตจฝญI]\s*\d{5})\s+รายวิชา\s*([^\n\t\r]+)',
                r'โครงสร้างรายวิชา\s*([^\n\t\r]+)\s*รหัสวิชา\s*([ทควสพศงอตจฝญI]\s*\d{5})'
            ]
            
            for pat in pats:
                for m in re.finditer(pat, doc_str_norm):
                    if pat == pats[1] or pat == pats[3]:
                        raw_c = m.group(2)
                        c_name = m.group(1).strip()
                    else:
                        raw_c = m.group(1)
                        c_name = m.group(2).strip() if m.group(2) else ""
                    
                    code = re.sub(r'\s+', '', raw_c)
                    c_name = re.sub(r'\s*กลุ่มสาระ.*$', '', c_name).strip()
                    c_name = re.sub(r'\s*ชั้น.*$', '', c_name).strip()
                    
                    if code not in courses_in_docx:
                        courses_in_docx[code] = {
                            'code': code,
                            'name': c_name,
                            'files': [os.path.basename(df)],
                            'has_desc': "คำอธิบายรายวิชา" in doc_str,
                            'has_structure': "โครงสร้างรายวิชา" in doc_str or "แผนการวัด" in doc_str or len(doc.tables) > 0,
                            'has_kpi': "ตัวชี้วัด" in doc_str or "ผลการเรียนรู้" in doc_str
                        }
                    else:
                        if os.path.basename(df) not in courses_in_docx[code]['files']:
                            courses_in_docx[code]['files'].append(os.path.basename(df))
                        if c_name and not courses_in_docx[code]['name']:
                            courses_in_docx[code]['name'] = c_name

            # Also check tables for courses
            for t in doc.tables:
                for row in t.rows:
                    r_text = " ".join([c.text.strip() for c in row.cells]).translate(thai_digits)
                    m_row = re.finditer(r'([ทควสพศงอตจฝญI]\s*\d{5})', r_text)
                    for m in m_row:
                        code = re.sub(r'\s+', '', m.group(1))
                        if code not in courses_in_docx:
                            courses_in_docx[code] = {
                                'code': code,
                                'name': '',
                                'files': [os.path.basename(df)],
                                'has_desc': False,
                                'has_structure': True,
                                'has_kpi': False
                            }
        except Exception as e:
            pass

    print(f"Total distinct course codes identified inside DOCX documents: {len(courses_in_docx)}")

    # 4. Check Vault
    vault_dir = os.path.join(cwd, 'Curriculum_Vault', '09_หลักสูตรสถานศึกษา')
    vault_files = glob.glob(f"{vault_dir}/**/*.md", recursive=True)
    vault_courses = {}
    for vf in vault_files:
        bname = os.path.basename(vf)
        if bname.startswith('00_'):
            continue
        m = re.match(r'^([ทควสพศงอตจฝญI]\d{5})', bname)
        if m:
            code = m.group(1)
            with open(vf, 'r', encoding='utf-8') as f:
                content = f.read()
            vault_courses[code] = {
                'code': code,
                'path': vf,
                'has_desc': "คำอธิบายรายวิชา" in content,
                'has_structure': "ตารางโครงสร้างรายวิชา" in content or "โครงสร้างรายวิชา" in content,
                'has_kpi': "ตัวชี้วัด" in content or "ผลการเรียนรู้" in content,
                'is_stub': len(content.strip().splitlines()) < 25
            }

    print(f"Total course Markdown files in Vault: {len(vault_courses)}")

    # 5. Check Matrix & Catalog
    matrix_path = os.path.join(cwd, 'school_courses_assessment_matrix.json')
    matrix = {}
    if os.path.exists(matrix_path):
        with open(matrix_path, 'r', encoding='utf-8') as f:
            matrix = json.load(f)
    print(f"Total courses in Assessment Matrix: {len(matrix)}")

    catalog_path = os.path.join(cwd, 'semester_catalog.json')
    catalog = {}
    if os.path.exists(catalog_path):
        with open(catalog_path, 'r', encoding='utf-8') as f:
            catalog = json.load(f)
    cat_courses = catalog.get('by_course_code', {})
    print(f"Total courses in Semester Catalog: {len(cat_courses)}")

    # 6. Detailed Comparison & Gap Analysis
    print("\n==================================================================")
    print("📊 COMPARISON & COVERAGE ANALYSIS")
    print("==================================================================")
    
    all_known_courses = set(excel_active_courses.keys()) | set(courses_in_docx.keys()) | set(vault_courses.keys()) | set(matrix.keys())
    print(f"Grand Total of all unique school courses ever referenced: {len(all_known_courses)}")
    print(f"Courses in Official Master Excel: {len(excel_active_courses)}")
    print(f"Courses in Vault: {len(vault_courses)}")
    print(f"Courses in Matrix: {len(matrix)}")

    # What courses are in Master Excel but NOT in Vault?
    excel_not_vault = set(excel_active_courses.keys()) - set(vault_courses.keys())
    print(f"\n❌ Active Excel Courses NOT in Vault ({len(excel_not_vault)}):")
    # Breakdown by subject
    subj_count = {}
    for c in sorted(excel_not_vault):
        prefix = c[0]
        subj_count[prefix] = subj_count.get(prefix, 0) + 1
    for p, cnt in sorted(subj_count.items()):
        print(f"   Prefix {p}: {cnt} courses")

    # Are these missing courses present in raw DOCX?
    in_docx_not_vault = excel_not_vault.intersection(courses_in_docx.keys())
    not_even_in_docx = excel_not_vault - set(courses_in_docx.keys())
    print(f"\n   -> Of these {len(excel_not_vault)} missing courses:")
    print(f"      - Available in raw DOCX files (ready to extract!): {len(in_docx_not_vault)} courses")
    print(f"      - Not found in raw DOCX (only defined in Excel structure): {len(not_even_in_docx)} courses")

    # Vault quality check
    stubs_in_vault = [c for c, v in vault_courses.items() if v['is_stub']]
    no_desc_vault = [c for c, v in vault_courses.items() if not v['has_desc']]
    no_kpi_vault = [c for c, v in vault_courses.items() if not v['has_kpi']]
    print(f"\n🔍 Vault Content Quality Check ({len(vault_courses)} files):")
    print(f"   - Stubs (< 25 lines): {len(stubs_in_vault)}")
    print(f"   - Missing Course Description (คำอธิบายรายวิชา): {len(no_desc_vault)}")
    print(f"   - Missing KPI/Learning Outcomes: {len(no_kpi_vault)}")

    # Details of in_docx_not_vault
    if in_docx_not_vault:
        print(f"\n📋 Sample courses in raw DOCX but not yet in Vault (Top 25):")
        for c in sorted(list(in_docx_not_vault))[:25]:
            d_info = courses_in_docx[c]
            ex_name = excel_active_courses.get(c, {}).get('name', '')
            print(f"   - {c}: {ex_name or d_info['name']} (found in {d_info['files'][0]})")

    # Save complete audit report JSON
    audit_data = {
        'total_active_excel_courses': len(excel_active_courses),
        'total_docx_courses': len(courses_in_docx),
        'total_vault_courses': len(vault_courses),
        'total_matrix_courses': len(matrix),
        'excel_not_in_vault': sorted(list(excel_not_vault)),
        'in_docx_not_vault': sorted(list(in_docx_not_vault)),
        'not_even_in_docx': sorted(list(not_even_in_docx)),
        'courses_in_docx': courses_in_docx
    }
    with open('reports/school_data_extraction_audit.json', 'w', encoding='utf-8') as f:
        json.dump(audit_data, f, ensure_ascii=False, indent=2)
    print("\n[OK] Full audit JSON saved to reports/school_data_extraction_audit.json")

if __name__ == '__main__':
    run_audit()
