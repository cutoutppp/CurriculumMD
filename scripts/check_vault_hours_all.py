import os
import glob
import re
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("school_courses_assessment_matrix.json", "r", encoding="utf-8") as f:
    matrix = json.load(f)

vault_root = os.path.join("Curriculum_Vault", "09_หลักสูตรสถานศึกษา")
files = glob.glob(f"{vault_root}/**/*.md", recursive=True)

print(f"Total files in vault: {len(files)}")

vault_data = {}
for vf in files:
    bn = os.path.basename(vf)
    if bn.startswith("00_"):
        continue
    m = re.match(r"^([ก-ฮa-zA-Z0-9]+)_(.*)\.md$", bn)
    code = m.group(1) if m else bn.replace(".md", "")
    with open(vf, "r", encoding="utf-8") as fp:
        txt = fp.read()
    
    # Try different regex for credits and hours
    m_cr = re.search(r"หน่วยกิต:\s*([0-9.]+)", txt)
    if not m_cr:
        m_cr = re.search(r"([0-9.]+)\s*หน่วยกิต", txt)
    
    m_h = re.search(r"เวลาเรียน:\s*([0-9]+)\s*ชั่วโมง", txt)
    if not m_h:
        m_h = re.search(r"([0-9]+)\s*ชั่วโมง", txt)
        
    cr = float(m_cr.group(1)) if m_cr else None
    h = int(m_h.group(1)) if m_h else None

    # Course name from frontmatter or heading
    m_n = re.search(r'^ชื่อรายวิชา:\s*\"?([^\n\r\"]+)\"?', txt, re.M)
    name = m_n.group(1).strip() if m_n else ""
    if not name:
        m_h1 = re.search(r'^#\s*([^\n\r]+)', txt, re.M)
        if m_h1:
            name = m_h1.group(1).replace(code, "").strip(" _-")

    vault_data[code] = {
        "file": vf,
        "name": name,
        "credits": cr,
        "hours": h
    }

print(f"Vault valid course files: {len(vault_data)}")

# Check diffs against matrix
diffs = []
for code, mc in sorted(matrix.items()):
    if code in vault_data:
        vd = vault_data[code]
        m_cr = float(mc.get("credits", 0))
        m_h = int(mc.get("total_hours", 0))
        v_cr = vd["credits"]
        v_h = vd["hours"]
        if v_cr is not None and v_h is not None:
            if m_cr != v_cr or m_h != v_h:
                diffs.append((code, mc.get("course_name"), m_cr, m_h, v_cr, v_h, vd["file"]))
        elif v_cr is not None and m_cr != v_cr:
            diffs.append((code, mc.get("course_name"), m_cr, m_h, v_cr, v_h, vd["file"]))
        elif v_h is not None and m_h != v_h:
            diffs.append((code, mc.get("course_name"), m_cr, m_h, v_cr, v_h, vd["file"]))

print(f"\nMatrix vs Vault Credit/Hour Diffs ({len(diffs)}):")
for d in diffs:
    print(f"  {d[0]} ({d[1]}): matrix={d[2]}cr/{d[3]}h  vault={d[4]}cr/{d[5]}h  path={d[6]}")
