# -*- coding: utf-8 -*-
"""
Synchronize school_courses_assessment_matrix.json and AssessmentHub
with the 100% restored secondary KPI mappings from kpi_data.js and semester_catalog.json.
"""
import os
import json
import re
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def sync_assessment_system():
    print("==================================================================")
    print("[SYNC] SYNCING ASSESSMENT PLAN SYSTEM WITH 100% KPI DATA")
    print("==================================================================")

    # 1. Load kpi_data.js
    with open('kpi_data.js', 'r', encoding='utf-8') as f:
        text = f.read()

    prefix = '/* Generated for Thailand Open Curriculum Portal */\nconst OPEN_CURRICULUM_DATA = '
    if text.startswith(prefix):
        json_text = text[len(prefix):].rstrip().rstrip(';')
    else:
        idx = text.find('{')
        json_text = text[idx:].rstrip().rstrip(';')

    kpi_data = json.loads(json_text)

    # KPI details map: code -> item
    kpi_map = {k['code']: k for k in kpi_data['kpis']}

    # Course to KPIs map: course_code -> list of kpi_codes
    course_to_kpis = {}
    for k in kpi_data['kpis']:
        for c_entry in k.get('courses', []):
            c_code = c_entry.split('_')[0]
            course_to_kpis.setdefault(c_code, []).append(k['code'])

    # 2. Load semester_catalog.json for course metadata
    with open('semester_catalog.json', 'r', encoding='utf-8') as f:
        catalog = json.load(f)
    catalog_by_code = catalog.get('by_course_code', {})

    # 3. Load school_courses_assessment_matrix.json
    with open('school_courses_assessment_matrix.json', 'r', encoding='utf-8') as f:
        matrix = json.load(f)

    print(f"Loaded {len(matrix)} courses from assessment matrix.")
    print(f"Total courses with mapped KPIs in curriculum: {len(course_to_kpis)}")

    # Area mapping
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

    # 4. Update existing courses in matrix
    updated_courses = 0
    added_courses = 0

    for c_code, kpi_codes in course_to_kpis.items():
        # Build full indicator formatted strings: f"{code} ({type}): {text}"
        formatted_indicators = []
        for kc in kpi_codes:
            if kc in kpi_map:
                k_item = kpi_map[kc]
                k_type = k_item.get('type', 'ตัวชี้วัด')
                k_text = k_item.get('text', '')
                formatted_indicators.append(f"{kc} ({k_type}): {k_text}")
            else:
                formatted_indicators.append(kc)

        if c_code in matrix:
            # Merge with existing indicators
            existing_inds = matrix[c_code].get('indicators', [])
            existing_codes = set()
            for ind in existing_inds:
                m = ind.split(' (')[0].split(':')[0].strip()
                existing_codes.add(m)

            new_indicators = list(existing_inds)
            for idx_k, kc in enumerate(kpi_codes):
                if kc not in existing_codes:
                    new_indicators.append(formatted_indicators[idx_k])

            matrix[c_code]['indicators'] = new_indicators

            # Ensure units exist and assign indicators to units
            units = matrix[c_code].get('units', [])
            if units:
                # 1. Check which KPI codes are currently in any unit
                assigned_kpis = set()
                for u in units:
                    for k_code in u.get('national_kpis', []):
                        assigned_kpis.add(k_code if isinstance(k_code, str) else k_code.get('code', ''))
                    for ind in u.get('indicators_raw', []):
                        m_code = ind.split(' (')[0].split(':')[0].strip()
                        assigned_kpis.add(m_code)

                # 2. For any KPI not yet assigned to a unit, assign to matching standard unit or best unit
                for kc in kpi_codes:
                    if kc not in assigned_kpis:
                        k_std = re.split(r'\s+[ปม]\.', kc)[0].strip() # e.g. "ค 2.1"
                        # Find unit that has matching standard
                        best_u = None
                        for u in units:
                            u_inds = u.get('national_kpis', []) + [x.split(' (')[0].split(':')[0].strip() for x in u.get('indicators_raw', [])]
                            if any(k_std in str(x) for x in u_inds):
                                best_u = u
                                break
                        if not best_u:
                            best_u = units[-1] # fallback to last unit
                        
                        # Add to best_u
                        if 'indicators_raw' not in best_u:
                            best_u['indicators_raw'] = []
                        f_ind = formatted_indicators[kpi_codes.index(kc)]
                        if f_ind not in best_u['indicators_raw']:
                            best_u['indicators_raw'].append(f_ind)
                        assigned_kpis.add(kc)

                # 3. Synchronize national_kpis on each unit from indicators_raw
                for u in units:
                    raw_inds = u.get('indicators_raw', [])
                    u_nk = list(u.get('national_kpis', []))
                    u_nk_set = set(x if isinstance(x, str) else x.get('code', '') for x in u_nk)
                    for ind in raw_inds:
                        code_match = ind.split(' (')[0].split(':')[0].strip()
                        if code_match and code_match not in u_nk_set:
                            u_nk.append(code_match)
                            u_nk_set.add(code_match)
                    u['national_kpis'] = u_nk

            updated_courses += 1
        else:
            # Course not in matrix, add it!
            cat_entry = catalog_by_code.get(c_code, {})
            name = cat_entry.get('name', c_code)
            area = PREFIX_AREA_MAP.get(c_code[0] if c_code else '', 'กลุ่มสาระการเรียนรู้')
            grade = cat_entry.get('grade', 'ม.1')
            if not grade or grade == 'Unknown':
                # infer from digit 2: e.g. ว21103 -> ม.1, ว22103 -> ม.2, ว31101 -> ม.4
                if len(c_code) >= 3:
                    d = c_code[1]
                    d2 = c_code[2]
                    if d == '2':
                        grade = f"ม.{d2}"
                    elif d == '3':
                        grade = f"ม.{int(d2)+3}"
            try:
                credits = float(cat_entry.get('credits', 1.0))
            except:
                credits = 1.0
            total_hours = int(credits * 40)
            target_pre_h = (total_hours // 2) - 1
            target_post_h = (total_hours // 2) - 1

            # Build 4 default units
            quarter = max(1, len(formatted_indicators) // 4)
            u1_raw = formatted_indicators[:quarter]
            u2_raw = formatted_indicators[quarter:quarter*2]
            u3_raw = formatted_indicators[quarter*2:quarter*3]
            u4_raw = formatted_indicators[quarter*3:]

            def extract_codes(raw_list):
                return [x.split(' (')[0].split(':')[0].strip() for x in raw_list]

            units = [
                {
                    "unit_no": "1",
                    "unit_name": "หน่วยการเรียนรู้ที่ 1",
                    "hours": target_pre_h // 2,
                    "score_k": 8, "score_p": 2, "score_a": 0, "score_total": 10,
                    "indicators_raw": u1_raw,
                    "national_kpis": extract_codes(u1_raw),
                    "key_concepts": []
                },
                {
                    "unit_no": "2",
                    "unit_name": "หน่วยการเรียนรู้ที่ 2",
                    "hours": target_pre_h - (target_pre_h // 2),
                    "score_k": 10, "score_p": 3, "score_a": 2, "score_total": 15,
                    "indicators_raw": u2_raw,
                    "national_kpis": extract_codes(u2_raw),
                    "key_concepts": []
                },
                {
                    "unit_no": "3",
                    "unit_name": "หน่วยการเรียนรู้ที่ 3",
                    "hours": target_post_h // 2,
                    "score_k": 7, "score_p": 5, "score_a": 3, "score_total": 15,
                    "indicators_raw": u3_raw,
                    "national_kpis": extract_codes(u3_raw),
                    "key_concepts": []
                },
                {
                    "unit_no": "4",
                    "unit_name": "หน่วยการเรียนรู้ที่ 4",
                    "hours": target_post_h - (target_post_h // 2),
                    "score_k": 6, "score_p": 2, "score_a": 2, "score_total": 10,
                    "indicators_raw": u4_raw,
                    "national_kpis": extract_codes(u4_raw),
                    "key_concepts": []
                }
            ]

            matrix[c_code] = {
                "course_code": c_code,
                "course_name": name,
                "learning_area": area,
                "normalized_area": area,
                "folder_name": AREA_TO_FOLDER.get(area, '00_ทั่วไป'),
                "grade_level": grade,
                "credits": credits,
                "total_hours": total_hours,
                "is_basic": True,
                "target_pre_hours": target_pre_h,
                "target_post_hours": target_post_h,
                "teachers": ["....................................................."],
                "units": units,
                "indicators": formatted_indicators,
                "is_scheduled_term2": True
            }
            added_courses += 1

    print(f"Updated {updated_courses} courses and added {added_courses} courses in matrix.")
    print(f"Total courses in matrix now: {len(matrix)}")

    # Save school_courses_assessment_matrix.json
    with open('school_courses_assessment_matrix.json', 'w', encoding='utf-8') as f:
        json.dump(matrix, f, ensure_ascii=False, indent=2)
    print("[OK] school_courses_assessment_matrix.json successfully saved!")

    # 5. Export to AssessmentHub if directory exists
    target_dir = r"c:\Users\peera\Desktop\Github_project\AssessmentHub\assessment-plan"
    if os.path.exists(target_dir):
        print("\nUpdating AssessmentHub data...")
        schedule_path = "semester2_teachers_mapping.json"
        schedule = {}
        if os.path.exists(schedule_path):
            with open(schedule_path, 'r', encoding='utf-8') as f:
                schedule = json.load(f)

        compiled_courses = {}
        for code, c in matrix.items():
            sch_entry = schedule.get(code, {})
            teachers = sch_entry.get("teachers", c.get("teachers", []))
            if not teachers:
                teachers = ["....................................................."]

            compiled_courses[code] = {
                "course_code": code,
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
                "is_scheduled_term2": code in schedule
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

        print(f"[OK] AssessmentHub updated ({len(compiled_courses)} courses written to {out_json} & {out_js})")

if __name__ == '__main__':
    sync_assessment_system()
