# -*- coding: utf-8 -*-
import os
import glob
import re
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

with open("school_courses_assessment_matrix.json", "r", encoding="utf-8") as f:
    matrix = json.load(f)

vault_root = os.path.join("Curriculum_Vault", "09_หลักสูตรสถานศึกษา")
vault_files = glob.glob(f"{vault_root}/**/*.md", recursive=True)

vault_data = {}
for vf in vault_files:
    bn = os.path.basename(vf)
    if bn.startswith("00_"):
        continue
    m = re.match(r"^([ก-ฮa-zA-Z0-9]+)_(.*)\.md$", bn)
    if m:
        code = m.group(1)
        fname = m.group(2)
    else:
        code = bn.replace(".md", "")
        fname = ""
    
    with open(vf, "r", encoding="utf-8") as fp:
        txt = fp.read()
    
    fm_name = ""
    fm_cr = None
    fm_h = None
    
    m_name = re.search(r'^ชื่อรายวิชา:\s*\"?([^\n\r\"]+)\"?', txt, re.M)
    if m_name:
        fm_name = m_name.group(1).strip()
    
    m_c = re.search(r'^หน่วยกิต:\s*([0-9.]+)', txt, re.M)
    if m_c:
        fm_cr = float(m_c.group(1))
    
    m_h = re.search(r'^เวลาเรียน:\s*([0-9]+)\s*ชั่วโมง', txt, re.M)
    if m_h:
        fm_h = int(m_h.group(1))
    
    vault_data[code] = {
        "name": fm_name or fname,
        "fname": fname,
        "credits": fm_cr,
        "hours": fm_h,
        "path": vf
    }

print(f"Total Vault courses: {len(vault_data)}")

# 1. Duplicates to delete from matrix
to_delete = sorted([c for c in matrix if c not in vault_data])
print(f"\n1. Courses in Matrix to DELETE (not in Vault): {to_delete}")
for c in to_delete:
    print(f"   {c}: {matrix[c].get('course_name')}")

# 2. Credits and hours differences
ch_diffs = []
for code, vd in sorted(vault_data.items()):
    if code in matrix:
        mc = matrix[code]
        m_cr = float(mc.get("credits", 0))
        m_h = int(mc.get("total_hours", 0))
        if vd["credits"] is not None and (m_cr != vd["credits"] or m_h != vd["hours"]):
            ch_diffs.append({
                "code": code,
                "name": mc.get("course_name"),
                "matrix_cr": m_cr,
                "vault_cr": vd["credits"],
                "matrix_h": m_h,
                "vault_h": vd["hours"]
            })

print(f"\n2. Credit/Hour Differences ({len(ch_diffs)}):")
for d in ch_diffs:
    print(f"   {d['code']} ({d['name']}): Matrix={d['matrix_cr']}cr/{d['matrix_h']}h  -->  Vault={d['vault_cr']}cr/{d['vault_h']}h")

# 3. Name differences
name_diffs = []
for code, vd in sorted(vault_data.items()):
    if code in matrix:
        mc = matrix[code]
        m_name = mc.get("course_name", "").strip()
        v_name = vd["name"].strip()
        if m_name != v_name:
            name_diffs.append({
                "code": code,
                "matrix_name": m_name,
                "vault_name": v_name,
                "fname": vd["fname"]
            })

print(f"\n3. Name Differences ({len(name_diffs)}):")
for d in name_diffs:
    print(f"   {d['code']}: Matrix='{d['matrix_name']}'  -->  Vault='{d['vault_name']}'")
