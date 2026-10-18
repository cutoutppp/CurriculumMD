# -*- coding: utf-8 -*-
import os
import json
import re

print("=== MIGRATING ส20250 -> ง20250 (ผลิตภัณฑ์งานปูน) ===")

curriculum_root = r"c:\Users\peera\Desktop\AntigravityProject\CurriculumMD"
hub_root = r"c:\Users\peera\Desktop\Github_project\AssessmentHub"

# 1. Update school_courses_assessment_matrix.json
m_path = os.path.join(curriculum_root, "school_courses_assessment_matrix.json")
with open(m_path, "r", encoding="utf-8") as f:
    matrix = json.load(f)

if "ส20250" in matrix:
    data = matrix.pop("ส20250")
    data["course_code"] = "ง20250"
    data["learning_area"] = "การงานอาชีพ"
    data["normalized_area"] = "การงานอาชีพ"
    data["folder_name"] = "07_การงานอาชีพ"
    matrix["ง20250"] = data
    print("[OK] Updated school_courses_assessment_matrix.json")

with open(m_path, "w", encoding="utf-8") as f:
    json.dump(matrix, f, ensure_ascii=False, indent=2)

# 2. Update semester_catalog.json
c_path = os.path.join(curriculum_root, "semester_catalog.json")
with open(c_path, "r", encoding="utf-8") as f:
    cat = json.load(f)

if "ส20250" in cat.get("by_course_code", {}):
    cdata = cat["by_course_code"].pop("ส20250")
    cat["by_course_code"]["ง20250"] = cdata
    print("[OK] Updated semester_catalog.json (by_course_code)")

by_sem = cat.get("by_semester", {})
for sem_name, sem_data in by_sem.items():
    for grp in ["basic", "elective"]:
        for item in sem_data.get(grp, []):
            if item.get("code") == "ส20250":
                item["code"] = "ง20250"
                print(f"[OK] Updated semester_catalog.json (by_semester {sem_name} {grp})")

with open(c_path, "w", encoding="utf-8") as f:
    json.dump(cat, f, ensure_ascii=False, indent=2)

# 3. Update extracted_school_course_descriptions.json
desc_path = os.path.join(curriculum_root, "extracted_school_course_descriptions.json")
if os.path.exists(desc_path):
    with open(desc_path, "r", encoding="utf-8") as f:
        descs = json.load(f)
    if "ส20250" in descs.get("by_code", {}):
        d_val = descs["by_code"].pop("ส20250")
        descs["by_code"]["ง20250"] = d_val
        print("[OK] Updated extracted_school_course_descriptions.json")
    with open(desc_path, "w", encoding="utf-8") as f:
        json.dump(descs, f, ensure_ascii=False, indent=2)

# 4. Rename & update markdown in Curriculum_Vault
vault_old = os.path.join(curriculum_root, "Curriculum_Vault", "09_หลักสูตรสถานศึกษา", "07_การงานอาชีพ", "ส20250_ผลิตภัณฑ์งานปูน.md")
vault_new = os.path.join(curriculum_root, "Curriculum_Vault", "09_หลักสูตรสถานศึกษา", "07_การงานอาชีพ", "ง20250_ผลิตภัณฑ์งานปูน.md")
if os.path.exists(vault_old):
    with open(vault_old, "r", encoding="utf-8") as f:
        content = f.read()
    content = content.replace("รหัสวิชา: ส20250", "รหัสวิชา: ง20250")
    content = content.replace("# ส20250 ผลิตภัณฑ์งานปูน", "# ง20250 ผลิตภัณฑ์งานปูน")
    content = content.replace("ส20250", "ง20250")
    with open(vault_new, "w", encoding="utf-8") as f:
        f.write(content)
    os.remove(vault_old)
    print("[OK] Renamed and updated Vault markdown file")

# 5. Update index & hub files
all_idx = os.path.join(curriculum_root, "Curriculum_Vault", "09_หลักสูตรสถานศึกษา", "00_ดัชนีรายวิชาทั้งหมด.md")
if os.path.exists(all_idx):
    with open(all_idx, "r", encoding="utf-8") as f:
        txt = f.read()
    txt = txt.replace("`ส20250`", "`ง20250`")
    txt = txt.replace("[[ส20250_ผลิตภัณฑ์งานปูน|ดูแผนวัด]]", "[[ง20250_ผลิตภัณฑ์งานปูน|ดูแผนวัด]]")
    with open(all_idx, "w", encoding="utf-8") as f:
        f.write(txt)
    print("[OK] Updated 00_ดัชนีรายวิชาทั้งหมด.md")

career_hub = os.path.join(curriculum_root, "Curriculum_Vault", "09_หลักสูตรสถานศึกษา", "07_การงานอาชีพ", "00_กลุ่มสาระ_การงานอาชีพ.md")
if os.path.exists(career_hub):
    with open(career_hub, "r", encoding="utf-8") as f:
        txt = f.read()
    txt = txt.replace("`ส20250`", "`ง20250`")
    txt = txt.replace("[[ส20250_ผลิตภัณฑ์งานปูน|เปิดแผนวัด ส20250]]", "[[ง20250_ผลิตภัณฑ์งานปูน|เปิดแผนวัด ง20250]]")
    with open(career_hub, "w", encoding="utf-8") as f:
        f.write(txt)
    print("[OK] Updated 00_กลุ่มสาระ_การงานอาชีพ.md")

# 6. Update text / sample / script files
for other_p in [
    os.path.join(curriculum_root, "SEMESTER_TEACHING_GUIDE.md"),
    os.path.join(curriculum_root, "uneven_courses_sample.txt"),
    os.path.join(curriculum_root, "fix_course_metadata_anomalies.py")
]:
    if os.path.exists(other_p):
        with open(other_p, "r", encoding="utf-8") as f:
            t = f.read()
        t = t.replace("ส20250", "ง20250")
        with open(other_p, "w", encoding="utf-8") as f:
            f.write(t)
        print(f"[OK] Updated {os.path.basename(other_p)}")

# 7. Update JS files in CurriculumMD
for js_p in [
    os.path.join(curriculum_root, "school_courses_data.js"),
    os.path.join(curriculum_root, "kpi_data.js")
]:
    if os.path.exists(js_p):
        with open(js_p, "r", encoding="utf-8") as f:
            t = f.read()
        t = t.replace('"ส20250"', '"ง20250"')
        t = t.replace("'ส20250'", "'ง20250'")
        t = t.replace("ส20250_ผลิตภัณฑ์งานปูน", "ง20250_ผลิตภัณฑ์งานปูน")
        with open(js_p, "w", encoding="utf-8") as f:
            f.write(t)
        print(f"[OK] Updated {os.path.basename(js_p)}")

# 8. Update AssessmentHub data files
hub_json = os.path.join(hub_root, "assessment-plan", "data", "courses_2_2569.json")
hub_js = os.path.join(hub_root, "assessment-plan", "data", "courses_2_2569.js")

if os.path.exists(hub_json):
    with open(hub_json, "r", encoding="utf-8") as f:
        hub_data = json.load(f)
    if "ส20250" in hub_data:
        h_item = hub_data.pop("ส20250")
        h_item["course_code"] = "ง20250"
        h_item["learning_area"] = "การงานอาชีพ"
        hub_data["ง20250"] = h_item
        print("[OK] Updated AssessmentHub courses_2_2569.json")
    with open(hub_json, "w", encoding="utf-8") as f:
        json.dump(hub_data, f, ensure_ascii=False, indent=2)

    with open(hub_js, "w", encoding="utf-8") as f:
        f.write("const COURSES_2_2569 = ")
        json.dump(hub_data, f, ensure_ascii=False)
        f.write(";\n")
    print("[OK] Updated AssessmentHub courses_2_2569.js")

print("=== ALL MIGRATION STEPS COMPLETE FOR ผลิตภัณฑ์งานปูน ===")
