# -*- coding: utf-8 -*-
import os
import glob
import re
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("school_courses_assessment_matrix.json", "r", encoding="utf-8") as f:
    matrix = json.load(f)

vault_root = os.path.join("Curriculum_Vault", "09_หลักสูตรสถานศึกษา")
vault_files = glob.glob(f"{vault_root}/**/*.md", recursive=True)

vault_courses = {}
for vf in vault_files:
    bn = os.path.basename(vf)
    if bn.startswith("00_"):
        continue
    m = re.match(r"^([ก-ฮa-zA-Z0-9]+)_(.*)\.md$", bn)
    if m:
        code = m.group(1)
        name_from_file = m.group(2)
    else:
        m2 = re.match(r"^([ก-ฮa-zA-Z0-9]+)\.md$", bn)
        code = m2.group(1)
        name_from_file = ""
    
    with open(vf, "r", encoding="utf-8") as fp:
        txt = fp.read()
    
    fm_name = ""
    fm_credits = None
    fm_hours = None
    
    m_name = re.search(r'^ชื่อรายวิชา:\s*\"?([^\n\r\"]+)\"?', txt, re.M)
    if m_name:
        fm_name = m_name.group(1).strip()
    
    m_c = re.search(r'^หน่วยกิต:\s*([0-9.]+)', txt, re.M)
    if m_c:
        fm_credits = float(m_c.group(1))
    
    m_h = re.search(r'^เวลาเรียน:\s*([0-9]+)\s*ชั่วโมง', txt, re.M)
    if m_h:
        fm_hours = int(m_h.group(1))
    
    vault_courses[code] = {
        "code": code,
        "name": fm_name or name_from_file,
        "file_name": name_from_file,
        "credits": fm_credits,
        "hours": fm_hours,
        "path": vf
    }

print(f"Total Vault courses parsed: {len(vault_courses)}")

# Extra in matrix
extra_in_matrix = sorted(list(set(matrix.keys()) - set(vault_courses.keys())))
print(f"\n--- Extra in Matrix ({len(extra_in_matrix)}) ---")
for c in extra_in_matrix:
    print(f"  {c}: {matrix[c].get('course_name')}")

# Extra in Vault
extra_in_vault = sorted(list(set(vault_courses.keys()) - set(matrix.keys())))
print(f"\n--- Extra in Vault ({len(extra_in_vault)}) ---")
for c in extra_in_vault:
    print(f"  {c}: {vault_courses[c].get('name')}")

# Compare credits & hours
credit_diffs = []
for code, vc in sorted(vault_courses.items()):
    if code in matrix:
        mc = matrix[code]
        m_cr = float(mc.get("credits", 0))
        v_cr = vc["credits"]
        m_h = int(mc.get("total_hours", 0))
        v_h = vc["hours"]
        if (v_cr is not None and m_cr != v_cr) or (v_h is not None and m_h != v_h):
            credit_diffs.append((code, mc.get("course_name"), m_cr, v_cr, m_h, v_h))

print(f"\n--- Credit/Hour Differences ({len(credit_diffs)}) ---")
for code, name, m_cr, v_cr, m_h, v_h in credit_diffs:
    print(f"  {code} ({name}): Matrix(cr={m_cr}, h={m_h}) vs Vault(cr={v_cr}, h={v_h})")

# Compare names
name_diffs = []
for code, vc in sorted(vault_courses.items()):
    if code in matrix:
        mc = matrix[code]
        m_name = mc.get("course_name", "").strip()
        v_name = vc["name"].strip()
        if m_name != v_name:
            name_diffs.append((code, m_name, v_name, vc["file_name"]))

print(f"\n--- Name Differences ({len(name_diffs)}) ---")
for code, m_name, v_name, fn in name_diffs:
    print(f"  {code}: Matrix=\"{m_name}\"  ==>  Vault=\"{v_name}\"")
