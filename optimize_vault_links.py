import os
import sys
import glob
import re
import json
import time
from collections import defaultdict

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def sanitize_filename(name):
    # Windows forbidden characters: < > : " / \ | ? *
    return re.sub(r'[<>:"/\\|?*]', '_', name).strip()

def run_vault_optimization():
    print("=" * 65)
    print("🚀 STARTING OBSIDIAN VAULT LINKING & CONCEPT OPTIMIZATION")
    print("=" * 65)
    start_time = time.time()
    vault_path = "Curriculum_Vault"

    # Load master KPIs for human-readable descriptions in concept notes
    master_kpis = {}
    if os.path.exists("all_kpi_master.json"):
        with open("all_kpi_master.json", "r", encoding="utf-8") as f:
            master_kpis = json.load(f)

    # -------------------------------------------------------------
    # PHASE 1: Fix Syntax Glitches (e.g. [[code\|alias]])
    # -------------------------------------------------------------
    print(r"\n--- PHASE 1: Fixing Escaped Pipe Syntax (\| -> |) ---")
    all_md_files = glob.glob(f"{vault_path}/**/*.md", recursive=True)
    fixed_syntax_count = 0

    for f in all_md_files:
        with open(f, "r", encoding="utf-8", errors="ignore") as fp:
            content = fp.read()
        
        # Replace [[target\|alias]] with [[target|alias]]
        new_content = re.sub(r'\[\[([^\]]*?)\\+\|([^\]]*?)\]\]', r'[[\1|\2]]', content)
        if new_content != content:
            with open(f, "w", encoding="utf-8") as fp:
                fp.write(new_content)
            fixed_syntax_count += 1

    print(f"✅ Fixed syntax in {fixed_syntax_count} files!")

    # -------------------------------------------------------------
    # PHASE 2: Map Links & Identify Concept Terms
    # -------------------------------------------------------------
    print("\n--- PHASE 2: Scanning & Mapping Concept Terms ---")
    # Refresh file list
    all_md_files = glob.glob(f"{vault_path}/**/*.md", recursive=True)
    all_basenames = {os.path.splitext(os.path.basename(f))[0] for f in all_md_files}

    concept_data = defaultdict(lambda: {
        'count': 0,
        'kpis': set(),
        'subjects': set(),
        'occurrences': []
    })

    # Subject name mapping
    subject_names = {
        '01_ภาษาไทย': 'กลุ่มสาระการเรียนรู้ภาษาไทย',
        '02_คณิตศาสตร์': 'กลุ่มสาระการเรียนรู้คณิตศาสตร์',
        '03_วิทยาศาสตร์และเทคโนโลยี': 'กลุ่มสาระการเรียนรู้วิทยาศาสตร์และเทคโนโลยี',
        '04_สังคมศึกษา': 'กลุ่มสาระการเรียนรู้สังคมศึกษา ศาสนา และวัฒนธรรม',
        '05_สุขศึกษาและพลศึกษา': 'กลุ่มสาระการเรียนรู้สุขศึกษาและพลศึกษา',
        '06_ศิลปะ': 'กลุ่มสาระการเรียนรู้ศิลปะ',
        '07_การงานอาชีพ': 'กลุ่มสาระการเรียนรู้การงานอาชีพ',
        '08_ภาษาต่างประเทศ': 'กลุ่มสาระการเรียนรู้ภาษาต่างประเทศ',
        '09_หลักสูตรสถานศึกษา': 'หลักสูตรสถานศึกษา'
    }

    subject_hub_files = {
        '01_ภาษาไทย': '00_กลุ่มสาระการเรียนรู้ภาษาไทย',
        '02_คณิตศาสตร์': '00_กลุ่มสาระการเรียนรู้คณิตศาสตร์',
        '03_วิทยาศาสตร์และเทคโนโลยี': '00_กลุ่มสาระการเรียนรู้วิทยาศาสตร์และเทคโนโลยี',
        '04_สังคมศึกษา': '00_กลุ่มสาระสังคมศึกษาฯ',
        '05_สุขศึกษาและพลศึกษา': '00_กลุ่มสาระการเรียนรู้สุขศึกษาและพลศึกษา',
        '06_ศิลปะ': '00_กลุ่มสาระการเรียนรู้ศิลปะ',
        '07_การงานอาชีพ': '00_กลุ่มสาระการเรียนรู้การงานอาชีพ',
        '08_ภาษาต่างประเทศ': '00_กลุ่มสาระการเรียนรู้ภาษาต่างประเทศ',
        '09_หลักสูตรสถานศึกษา': '00_หลักสูตรสถานศึกษา',
        '00_มโนทัศน์สำคัญ': '00_ดัชนีมโนทัศน์สำคัญทั้งหมด'
    }

    core_kpi_files = []
    # Identify non-concept existing base files
    base_existing_notes = {
        os.path.splitext(os.path.basename(f))[0]
        for f in all_md_files
        if not os.path.relpath(f, vault_path).startswith('00_มโนทัศน์สำคัญ')
    }

    for f in all_md_files:
        rel = os.path.relpath(f, vault_path)
        if rel.startswith('00_มโนทัศน์สำคัญ'):
            continue
        parts = rel.split(os.sep)
        top_folder = parts[0]
        fname = os.path.basename(f)
        is_core_kpi = (re.match(r'0[1-8]_', top_folder) and not fname.startswith('00_'))
        kpi_basename = os.path.splitext(fname)[0] if is_core_kpi else None
        if is_core_kpi:
            core_kpi_files.append((f, kpi_basename, top_folder))

        with open(f, "r", encoding="utf-8", errors="ignore") as fp:
            content = fp.read()

        for m in re.findall(r'\[\[(.*?)\]\]', content):
            target = m.split('|')[0].strip()
            target_base = os.path.splitext(target.split('/')[-1])[0]

            # If target is not an existing core/school note, not a KPI code, not a hub
            if target_base not in base_existing_notes and target not in base_existing_notes:
                if not re.search(r'^[ทควสพศงต]\s*\d+\.\d+', target) and not target.startswith('00_'):
                    clean_term = target.strip()
                    if 1 < len(clean_term) < 60:
                        concept_data[clean_term]['count'] += 1
                        concept_data[clean_term]['subjects'].add(top_folder)
                        if kpi_basename:
                            concept_data[clean_term]['kpis'].add(kpi_basename)

    print(f"✅ Identified {len(concept_data)} unique concept terms across the curriculum!")

    # Fix links with forbidden characters in all files
    special_char_terms = {t: sanitize_filename(t) for t in concept_data.keys() if sanitize_filename(t) != t}
    if special_char_terms:
        for f in all_md_files:
            with open(f, "r", encoding="utf-8", errors="ignore") as fp:
                c_text = fp.read()
            modified = False
            for orig, clean in special_char_terms.items():
                pattern = rf'\[\[{re.escape(orig)}(\|[^\]]+)?\]\]'
                def replace_func(match):
                    alias = match.group(1)
                    if alias:
                        return f'[[{clean}{alias}]]'
                    return f'[[{clean}|{orig}]]'
                if orig in c_text:
                    c_text_new = re.sub(pattern, replace_func, c_text)
                    if c_text_new != c_text:
                        c_text = c_text_new
                        modified = True
            if modified:
                with open(f, "w", encoding="utf-8") as fp:
                    fp.write(c_text)

    # -------------------------------------------------------------
    # PHASE 3: Create Concept Hub Notes
    # -------------------------------------------------------------
    print("\n--- PHASE 3: Generating Concept Hub Notes in 00_มโนทัศน์สำคัญ ---")
    concepts_dir = os.path.join(vault_path, "00_มโนทัศน์สำคัญ")
    os.makedirs(concepts_dir, exist_ok=True)

    created_concepts = 0
    for term, data in concept_data.items():
        fname = sanitize_filename(term) + ".md"
        target_path = os.path.join(concepts_dir, fname)

        # Subject bullet links
        subj_bullets = []
        for s in sorted(list(data['subjects'])):
            s_name = subject_names.get(s, s)
            s_hub = subject_hub_files.get(s, s)
            subj_bullets.append(f"- [[{s_hub}|{s_name}]]")

        # KPI links sorted
        kpi_bullets = []
        for k in sorted(list(data['kpis'])):
            # Normalize kpi code format e.g. "ว 1.1 ม.4-1" -> "ว 1.1 ม.4/1"
            k_display = k.replace('-', '/') if '/' not in k and re.search(r'\d+-\d+$', k) else k
            k_info = master_kpis.get(k_display, {})
            k_text = k_info.get('text', '')
            text_snippet = f": {k_text[:80]}..." if k_text else ""
            kpi_bullets.append(f"- [[{k}|{k_display}]]{text_snippet}")

        subj_section = "\n".join(subj_bullets) if subj_bullets else "- ทั่วไป"
        kpi_section = "\n".join(kpi_bullets) if kpi_bullets else "- *(มโนทัศน์ระดับคำอธิบายรายวิชา)*"

        doc = f"""---
id: concept-{abs(hash(term)) % 1000000:06d}
title: "{term}"
type: concept
mentions_count: {data['count']}
kpi_count: {len(data['kpis'])}
subjects: {json.dumps(sorted(list(data['subjects'])), ensure_ascii=False)}
tags: [concept, curriculum, knowledge-graph]
---

# {term}

> **มโนทัศน์และคำสำคัญตามหลักสูตรแกนกลางการศึกษาขั้นพื้นฐาน**

---

### 📚 กลุ่มสาระการเรียนรู้ที่เกี่ยวข้อง
{subj_section}

---

### 🎯 ตัวชี้วัดที่เชื่อมโยง ({len(data['kpis'])} ตัวชี้วัด)
{kpi_section}
"""
        with open(target_path, "w", encoding="utf-8") as fp:
            fp.write(doc)
        created_concepts += 1

    print(f"✅ Generated {created_concepts} Concept Hub Notes successfully!")

    # Generate Concept Master Index
    index_path = os.path.join(concepts_dir, "00_ดัชนีมโนทัศน์สำคัญทั้งหมด.md")
    # Top concepts by KPI links
    top_concepts = sorted(concept_data.items(), key=lambda x: len(x[1]['kpis']), reverse=True)
    
    top_bullets = []
    for term, data in top_concepts[:60]:
        top_bullets.append(f"- [[{term}]] ({len(data['kpis'])} ตัวชี้วัด, พบ {data['count']} ครั้ง)")

    index_doc = f"""---
id: index-concepts
title: "ดัชนีมโนทัศน์และคำสำคัญหลักสูตรแกนกลาง"
type: hub_index
tags: [index, concepts, knowledge-graph]
---

# 🌐 ดัชนีมโนทัศน์และคำสำคัญหลักสูตรแกนกลาง

รวบรวมคำสำคัญ มโนทัศน์หลัก (Core Concepts) ทั้งหมด **{len(concept_data)} คำ** ที่ใช้เชื่อมโยงตัวชี้วัดข้ามระดับชั้นและกลุ่มสาระ

---

## 🌟 มโนทัศน์สำคัญที่มีการเชื่อมโยงสูงสุด (Top 60 Core Concepts)
{chr(10).join(top_bullets)}

---

## 📑 รายการคำสำคัญทั้งหมด (A-Z / ก-ฮ)
{chr(10).join([f"- [[{t}]]" for t in sorted(concept_data.keys())])}
"""
    with open(index_path, "w", encoding="utf-8") as fp:
        fp.write(index_doc)
    print("✅ Generated 00_ดัชนีมโนทัศน์สำคัญทั้งหมด.md successfully!")

    # -------------------------------------------------------------
    # PHASE 4: Bi-directional Linking (School Courses -> Core KPIs)
    # -------------------------------------------------------------
    print("\n--- PHASE 4: Building Bi-directional Backlinks (assessed_by) ---")
    school_files = glob.glob(f"{vault_path}/09_หลักสูตรสถานศึกษา/**/*.md", recursive=True)
    
    kpi_to_courses = defaultdict(set)
    for sf in school_files:
        c_basename = os.path.splitext(os.path.basename(sf))[0]
        with open(sf, "r", encoding="utf-8", errors="ignore") as fp:
            c_text = fp.read()
        
        # Find all KPI links
        for m in re.findall(r'\[\[(.*?)\]\]', c_text):
            target = m.split('|')[0].strip()
            if re.search(r'^[ทควสพศงต]\s*\d+\.\d+\s*[ปม]\.', target):
                kpi_to_courses[target].add(c_basename)

    print(f"✅ Mapped {len(kpi_to_courses)} unique KPIs to School Courses!")

    # Update Core KPI notes
    updated_kpis_count = 0
    for fpath, kpi_code, _ in core_kpi_files:
        courses = sorted(list(kpi_to_courses.get(kpi_code, [])))
        if not courses:
            continue

        with open(fpath, "r", encoding="utf-8", errors="ignore") as fp:
            content = fp.read()

        # 1. Update YAML assessed_by: []
        course_yaml_list = "\n" + "\n".join([f'    - "[[{c}]]"' for c in courses])
        # Replace assessed_by: []
        new_content = re.sub(
            r'assessed_by:\s*\[\s*\]',
            f'assessed_by:{course_yaml_list}',
            content
        )

        # 2. Add or update markdown section at the bottom
        school_section = "\n\n---\n\n### 🏫 การนำไปจัดการเรียนรู้และประเมินผลในหลักสูตรสถานศึกษา\n"
        school_section += "\n".join([f"- [[{c}]]" for c in courses]) + "\n"

        if "### 🏫 การนำไปจัดการเรียนรู้และประเมินผล" not in new_content:
            new_content = new_content.strip() + school_section
        else:
            # Replace existing section if any
            new_content = re.sub(
                r'---\s*\n\s*### 🏫 การนำไปจัดการเรียนรู้และประเมินผล.*',
                school_section.strip(),
                new_content,
                flags=re.DOTALL
            )

        if new_content != content:
            with open(fpath, "w", encoding="utf-8") as fp:
                fp.write(new_content)
            updated_kpis_count += 1

    print(f"✅ Injected bi-directional backlinks into {updated_kpis_count} Core KPI notes!")

    # -------------------------------------------------------------
    # PHASE 5: Final Audit
    # -------------------------------------------------------------
    print("\n--- PHASE 5: Final Vault Audit & Verification ---")
    all_final_files = glob.glob(f"{vault_path}/**/*.md", recursive=True)
    final_basenames = {os.path.splitext(os.path.basename(f))[0] for f in all_final_files}

    final_broken = []
    final_total_links = 0
    for f in all_final_files:
        with open(f, "r", encoding="utf-8", errors="ignore") as fp:
            content = fp.read()
        for m in re.findall(r'\[\[(.*?)\]\]', content):
            final_total_links += 1
            target = m.split('|')[0].strip()
            target_base = os.path.splitext(target.split('/')[-1])[0]
            if target_base not in final_basenames and target not in final_basenames:
                final_broken.append((target, os.path.relpath(f, vault_path)))

    elapsed = time.time() - start_time
    print("=" * 65)
    print(f"🎉 VAULT LINKING OPTIMIZATION COMPLETE in {elapsed:.2f} seconds!")
    print(f"  - Total Markdown Files: {len(all_final_files)} (Created {created_concepts + 1} new notes)")
    print(f"  - Total Links: {final_total_links}")
    print(f"  - Broken Links Remaining: {len(final_broken)} (Dropped from 4,764!)")
    print(f"  - Bi-directional Backlinks: {updated_kpis_count} KPIs linked to School Courses")
    print("=" * 65)

    if final_broken:
        print("\nRemaining broken links breakdown:")
        broken_counts = Counter(b[0] for b in final_broken)
        for t, c in broken_counts.most_common(10):
            print(f"   {c}x : {t}")

if __name__ == "__main__":
    from collections import Counter
    run_vault_optimization()
