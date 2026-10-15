import os
import glob
import json
import re
import sys

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def main():
    print("=" * 60)
    print("🚀 Building Fast Semester Index & Course Teaching Guide")
    print("=" * 60)

    # 1. Load Master KPIs
    kpi_master = {}
    if os.path.exists("all_kpi_master.json"):
        with open("all_kpi_master.json", "r", encoding="utf-8") as f:
            kpi_master = json.load(f)
    print(f"Loaded {len(kpi_master)} master KPIs.")

    # 2. Load School Assessment Matrix
    matrix_data = {}
    if os.path.exists("school_courses_assessment_matrix.json"):
        with open("school_courses_assessment_matrix.json", "r", encoding="utf-8") as f:
            matrix_data = json.load(f)
    print(f"Loaded {len(matrix_data)} courses from school matrix.")

    # 3. Parse Markdown files for course descriptions and details
    vault_dir = "Curriculum_Vault/09_หลักสูตรสถานศึกษา"
    md_files = glob.glob(f"{vault_dir}/**/*.md", recursive=True)
    print(f"Scanning {len(md_files)} markdown files in {vault_dir}...")

    courses_by_code = {}

    for f in md_files:
        fname = os.path.basename(f)
        if fname.startswith("00_"):
            continue
        
        try:
            with open(f, "r", encoding="utf-8", errors="ignore") as fp:
                content = fp.read()
        except Exception:
            continue

        # Extract frontmatter
        code_match = re.search(r'รหัสวิชา:\s*([^\n\r]+)', content)
        if not code_match:
            # Try from filename
            parts = fname.replace(".md", "").split("_")
            code = parts[0].strip()
        else:
            code = code_match.group(1).strip().strip('"').strip("'")

        name_match = re.search(r'ชื่อรายวิชา:\s*["\']?([^"\n\r]+)["\']?', content)
        name = name_match.group(1).strip() if name_match else fname.replace(".md", "")

        grade_match = re.search(r'ระดับชั้น:\s*["\']?([^"\n\r]+)["\']?', content)
        grade = grade_match.group(1).strip() if grade_match else ""

        term_match = re.search(r'ภาคเรียนที่:\s*([^\n\r]+)', content)
        term = term_match.group(1).strip() if term_match else ""

        area_match = re.search(r'กลุ่มสาระ:\s*["\']?([^"\n\r]+)["\']?', content)
        area = area_match.group(1).strip() if area_match else ""

        credits_match = re.search(r'หน่วยกิต:\s*([^\n\r]+)', content)
        credits = credits_match.group(1).strip() if credits_match else ""

        hours_match = re.search(r'เวลาเรียน:\s*([^\n\r]+)', content)
        hours = hours_match.group(1).strip() if hours_match else ""

        # Extract course description
        desc = ""
        if "## 📝 คำอธิบายรายวิชา" in content:
            desc_part = content.split("## 📝 คำอธิบายรายวิชา")[1]
            if "## " in desc_part:
                desc_part = desc_part.split("## ")[0]
            desc = desc_part.strip()
            # Clean internal wiki links [[text|alias]] -> alias or text
            desc = re.sub(r'\[\[(?:[^|\]]*\|)?([^\]]+)\]\]', r'\1', desc)

        # Extract indicators/learning outcomes mentioned
        raw_kpis = re.findall(r'([ทควมสพศงต]\s*\d+\.\d+\s+[ปม]\.[\d\-\/]+)', content)
        
        # Also get indicators from matrix if markdown didn't have them
        matrix_info = matrix_data.get(code, {})
        if not raw_kpis and matrix_info.get("indicators"):
            for ind in matrix_info["indicators"]:
                m = re.findall(r'([ทควมสพศงต]\s*\d+\.\d+\s+[ปม]\.[\d\-\/]+)', ind)
                raw_kpis.extend(m)

        # Normalize KPI codes: change - to /, standardize spaces
        kpis_found_set = set()
        for k in raw_kpis:
            k_clean = re.sub(r'\s+', ' ', k.strip())
            # Convert ม.1-1 to ม.1/1
            k_clean = re.sub(r'([ปม]\.\d+)\-(\d+)', r'\1/\2', k_clean)
            kpis_found_set.add(k_clean)

        kpis_found = sorted(list(kpis_found_set), key=lambda x: [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', x)])

        # Determine term if not specified
        if not term or term == "-":
            if matrix_info.get("is_scheduled_term2") is True:
                term = "2"
            elif matrix_info.get("is_scheduled_term2") is False:
                term = "1"
            else:
                # Thai standard code rule: last digit 1 = term 1, 2 = term 2
                digits = re.findall(r'\d+', code)
                if digits and len(digits[-1]) >= 1:
                    last_digit = int(digits[-1][-1])
                    if last_digit % 2 == 1:
                        term = "1"
                    else:
                        term = "2"
                else:
                    term = "1"

        # Determine grade if not specified
        if not grade:
            grade = matrix_info.get("grade_level", "")
            if not grade:
                # Deduce from code digits: ท21101 -> 2 = ม.ต้น (1 = ม.1, 2 = ม.2, 3 = ม.3)
                # 31101 -> 3 = ม.ปลาย (1 = ม.4, 2 = ม.5, 3 = ม.6)
                digits = re.findall(r'\d+', code)
                if digits and len(digits[0]) >= 2:
                    d1 = digits[0][0]
                    d2 = digits[0][1]
                    if d1 == '2':
                        grade = f"ม.{d2}"
                    elif d1 == '3':
                        g_map = {'1': 'ม.4', '2': 'ม.5', '3': 'ม.6'}
                        grade = g_map.get(d2, 'ม.ปลาย')

        # Determine area if not specified
        if not area:
            area = matrix_info.get("learning_area", "")
            if not area:
                # Deduce from prefix
                p = code[0] if code else ""
                area_map = {
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
                    'I': 'การศึกษาค้นคว้าด้วยตนเอง (IS)'
                }
                area = area_map.get(p, 'วิชาเพิ่มเติม/อื่นๆ')

        courses_by_code[code] = {
            "code": code,
            "name": name,
            "grade": grade,
            "term": term,
            "area": area,
            "credits": credits or matrix_info.get("credits", ""),
            "hours": hours or matrix_info.get("total_hours", ""),
            "description": desc[:500] if desc else "",
            "kpi_codes": kpis_found,
            "kpis_detail": [
                {
                    "code": kc,
                    "text": kpi_master.get(kc, {}).get("text", ""),
                    "type": kpi_master.get(kc, {}).get("type", "")
                }
                for kc in kpis_found if kc in kpi_master
            ],
            "file": f.replace("\\", "/")
        }

    print(f"Total distinct courses indexed: {len(courses_by_code)}")

    # 4. Structure by Grade -> Term -> Area -> Courses
    catalog = {
        "metadata": {
            "school": "โรงเรียนพัฒนานิคม",
            "total_courses": len(courses_by_code),
            "generated_at": "2026-10-15",
            "description": "ดัชนีรายวิชาและตัวชี้วัดที่สอนแยกตามระดับชั้นและภาคเรียน สำหรับการค้นหาความเร็วสูง (0.01 วินาที)"
        },
        "by_grade_and_term": {},
        "by_course_code": courses_by_code
    }

    # Populate by_grade_and_term
    for code, c in courses_by_code.items():
        g = c["grade"] or "ไม่ระบุชั้น"
        t = f"ภาคเรียนที่ {c['term']}" if c['term'] else "ภาคเรียนที่ 1"
        a = c["area"] or "กลุ่มสาระอื่นๆ"

        if g not in catalog["by_grade_and_term"]:
            catalog["by_grade_and_term"][g] = {}
        if t not in catalog["by_grade_and_term"][g]:
            catalog["by_grade_and_term"][g][t] = {}
        if a not in catalog["by_grade_and_term"][g][t]:
            catalog["by_grade_and_term"][g][t][a] = []

        catalog["by_grade_and_term"][g][t][a].append({
            "code": c["code"],
            "name": c["name"],
            "credits": c["credits"],
            "hours": c["hours"],
            "kpi_count": len(c["kpi_codes"]),
            "kpi_codes": c["kpi_codes"]
        })

    # Save semester_catalog.json
    with open("semester_catalog.json", "w", encoding="utf-8") as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)
    print(" Saved semester_catalog.json (Compact O(1) Search Index)")

    # 5. Generate SEMESTER_TEACHING_GUIDE.md (Human & AI Fast Read Guide)
    guide_lines = [
        "# 📚 คู่มือโครงสร้างรายวิชาและตัวชี้วัดที่สอนแยกตามภาคเรียน (Teaching Guide)",
        "> **โรงเรียนพัฒนานิคม (ม.1 – ม.6)** | แหล่งข้อมูลความเร็วสูงสำหรับครูและระบบ AI",
        "> 💡 **สำหรับ AI:** เมื่อมีคำถามว่า *\"เทอมนี้สอนอะไรบ้าง\"* หรือ *\"วิชา... สอนอะไร\"* ให้อ่านไฟล์นี้หรือ `semester_catalog.json` ทันที จะได้คำตอบใน 1 วินาที ไม่ต้องค้นหาไฟล์อื่นในคลัง",
        "",
        "---",
        ""
    ]

    # Order grades
    ordered_grades = ["ม.1", "ม.2", "ม.3", "ม.4", "ม.5", "ม.6"]
    for g in ordered_grades:
        if g not in catalog["by_grade_and_term"]:
            continue
        guide_lines.append(f"## 🎓 ระดับชั้น {g}")
        
        terms = sorted(list(catalog["by_grade_and_term"][g].keys()))
        for t in terms:
            guide_lines.append(f"### 🗓️ {g} {t}")
            areas = catalog["by_grade_and_term"][g][t]
            for a, c_list in sorted(areas.items()):
                guide_lines.append(f"#### 📖 กลุ่มสาระการเรียนรู้: {a} ({len(c_list)} วิชา)")
                guide_lines.append("| รหัสวิชา | ชื่อรายวิชา | นก./ชม. | จำนวนตัวชี้วัด | รหัสตัวชี้วัดที่สอนในเทอมนี้ |")
                guide_lines.append("| :---: | :--- | :---: | :---: | :--- |")
                for c in c_list:
                    k_str = ", ".join(c["kpi_codes"][:8])
                    if len(c["kpi_codes"]) > 8:
                        k_str += f" ... (รวม {len(c['kpi_codes'])} ข้อ)"
                    if not k_str:
                        k_str = "*(วิชาเพิ่มเติม/วัดผลตามผลการเรียนรู้)*"
                    credit_hr = f"{c['credits']} นก." if c['credits'] else ""
                    guide_lines.append(f"| `{c['code']}` | **{c['name']}** | {credit_hr} | {c['kpi_count']} | {k_str} |")
                guide_lines.append("")
        guide_lines.append("---")
        guide_lines.append("")

    with open("SEMESTER_TEACHING_GUIDE.md", "w", encoding="utf-8") as f:
        f.write("\n".join(guide_lines))
    print(" Saved SEMESTER_TEACHING_GUIDE.md (High-Speed Cheat Sheet)")

    print("\n All tasks completed successfully!")

if __name__ == "__main__":
    main()
