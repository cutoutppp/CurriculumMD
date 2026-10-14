import os
import sys
import json
import glob
import re
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

matrix_json_path = r"c:\Users\peera\Desktop\AntigravityProject\CurriculumMD\school_courses_assessment_matrix.json"
vault_base = r"c:\Users\peera\Desktop\AntigravityProject\CurriculumMD\Curriculum_Vault\09_หลักสูตรสถานศึกษา"

with open(matrix_json_path, 'r', encoding='utf-8') as f:
    courses = json.load(f)

# Group by normalized area and folder
area_courses = defaultdict(list)
kpi_to_courses = defaultdict(list)

AREA_TO_FOLDER_MAP = {
    'ภาษาไทย': '01_ภาษาไทย',
    'คณิตศาสตร์': '02_คณิตศาสตร์',
    'วิทยาศาสตร์และเทคโนโลยี': '03_วิทยาศาสตร์และเทคโนโลยี',
    'สังคมศึกษา ศาสนา และวัฒนธรรม': '04_สังคมศึกษา',
    'สุขศึกษาและพลศึกษา': '05_สุขศึกษาและพลศึกษา',
    'ศิลปะ': '06_ศิลปะ',
    'การงานอาชีพ': '07_การงานอาชีพ',
    'ภาษาต่างประเทศ': '08_ภาษาต่างประเทศ'
}

for code, cdata in courses.items():
    area = cdata.get('normalized_area') or cdata.get('learning_area', '')
    folder = cdata.get('folder_name', '')
    if not folder:
        folder = AREA_TO_FOLDER_MAP.get(area, '')
    area_courses[folder].append(cdata)
    
    # Map KPIs
    for u in cdata.get('units', []):
        for kpi in u.get('national_kpis', []):
            k_code = kpi['code'] if isinstance(kpi, dict) else kpi
            kpi_to_courses[k_code].append({
                'course_code': code,
                'course_name': cdata.get('course_name', ''),
                'unit_no': u.get('unit_no'),
                'unit_name': u.get('unit_name'),
                'hours': u.get('hours'),
                'total_score': u.get('score_total'),
                'k': u.get('score_k'),
                'p': u.get('score_p'),
                'a': u.get('score_a')
            })

print(f"Total courses: {len(courses)}")
print(f"Total distinct national KPIs mapped to school courses: {len(kpi_to_courses)}")

# 1. Generate 00_ระบบแผนการวัดและประเมินผล.md
sys_hub_path = os.path.join(vault_base, "00_ระบบแผนการวัดและประเมินผล.md")
sys_md = """---
title: "ระบบแผนการวัดและประเมินผลการเรียนรู้ โรงเรียนพัฒนานิคม"
type: "assessment_system_hub"
academic_years: "2569–2571"
total_courses: {total_courses}
total_learning_units: {total_units}
total_kpi_mappings: {total_kpi_mappings}
tags: [assessment_system, curriculum_mapping, kpa_matrix, โรงเรียนพัฒนานิคม]
---

# 📊 ระบบแผนการวัดและประเมินผลการเรียนรู้ (Learning Assessment & Measurement System)
### โรงเรียนพัฒนานิคม สำนักงานเขตพื้นที่การศึกษามัธยมศึกษาลพบุรี (ปีการศึกษา ๒๕๖๙–๒๕๗๑)

> ย้อนกลับ: [[00_หลักสูตรสถานศึกษา]] | [[00_ดัชนีรายวิชาทั้งหมด]] | [[00_สารบัญหลักสูตรแกนกลาง]]

---

## 🧭 วัตถุประสงค์และภาพรวมของระบบ
ระบบแผนการวัดและประเมินผลการเรียนรู้นี้ จัดทำขึ้นโดยถอดรหัสโครงสร้างรายวิชาและแผนการวัดผลจากหลักสูตรกลุ่มสาระการเรียนรู้ทั้ง 8 กลุ่มสาระฯ ของโรงเรียนพัฒนานิคม จำนวน **{total_courses} รายวิชา** รวม **{total_units} หน่วยการเรียนรู้** เพื่อใช้เป็น **ฐานข้อมูลกลาง (Single Source of Truth)** ในการ:
1. **จัดทำแผนการจัดการเรียนรู้ (Lesson Plans):** ครูผู้สอนสามารถดึงตัวชี้วัดระหว่างทาง/ปลายทาง สาระสำคัญ และเวลาเรียนไปใช้สร้างแผนการจัดการเรียนรู้ได้ทันที
2. **ออกแบบแผนการวัดและประเมินผล (Assessment Blueprints):** กำหนดน้ำหนักคะแนนด้านความรู้ (K), กระบวนการ/ทักษะปฏิบัติ (P), และเจตคติ/คุณลักษณะ (A) ได้อย่างแม่นยำตามสัดส่วน 70:30 หรือ 80:20
3. **เชื่อมโยงตัวชี้วัด สพฐ. ๒๕๖๖ ครบวงจร:** เชื่อมโยงตัวชี้วัดระหว่างทางและปลายทางกลับไปยังเอกสารวิเคราะห์ตัวชี้วัดแกนกลาง 2,056 ตัวชี้วัดแบบสองทาง (Bidirectional Wiki-links)

---

## 📈 สรุปจำนวนรายวิชาและโครงสร้างแผนวัดจำแนกตามกลุ่มสาระการเรียนรู้

| ลำดับ | กลุ่มสาระการเรียนรู้ | โฟลเดอร์ในระบบ | จำนวนรายวิชา | จำนวนหน่วยการเรียนรู้ | สัดส่วนการประเมิน (K:P:A / กลางภาค:ปลายภาค) |
| :---: | :--- | :--- | :---: | :---: | :--- |
""".format(
    total_courses=len(courses),
    total_units=sum(len(c.get('units', [])) for c in courses.values()),
    total_kpi_mappings=len(kpi_to_courses)
)

area_order = [
    ('01_ภาษาไทย', 'ภาษาไทย'),
    ('02_คณิตศาสตร์', 'คณิตศาสตร์'),
    ('03_วิทยาศาสตร์และเทคโนโลยี', 'วิทยาศาสตร์และเทคโนโลยี'),
    ('04_สังคมศึกษา', 'สังคมศึกษา ศาสนา และวัฒนธรรม'),
    ('05_สุขศึกษาและพลศึกษา', 'สุขศึกษาและพลศึกษา'),
    ('06_ศิลปะ', 'ศิลปะ'),
    ('07_การงานอาชีพ', 'การงานอาชีพ'),
    ('08_ภาษาต่างประเทศ', 'ภาษาต่างประเทศ')
]

for idx, (folder, name) in enumerate(area_order, 1):
    c_list = area_courses.get(folder, [])
    u_count = sum(len(c.get('units', [])) for c in c_list)
    sys_md += f"| {idx} | **{name}** | [[00_กลุ่มสาระ_{name}|{folder}]] | **{len(c_list)}** วิชา | {u_count} หน่วย | ระหว่างภาค 70–80 : ปลายภาค 20–30 |\n"

sys_md += f"""| | **รวมทั้งสิ้น** | | **{len(courses)}** วิชา | **{sum(len(c.get('units', [])) for c in courses.values())}** หน่วย | **100 คะแนนเต็ม** |

---

## 🎯 โครงสร้างมิติการประเมิน (Assessment Dimensions: K - P - A)

```mermaid
flowchart TD
    A["คะแนนรวม 100 คะแนน"] --> B["คะแนนระหว่างภาคเรียน (70 - 80 คะแนน)"]
    A --> C["คะแนนปลายภาคเรียน (20 - 30 คะแนน)"]
    
    B --> B1["หน่วยการเรียนรู้ (Formative Units)"]
    B --> B2["สอบกลางภาคเรียน (Midterm Exam)"]
    
    B1 --> K["K: ด้านความรู้ (Knowledge)<br>ทดสอบ, ใบงาน, ตอบคำถาม"]
    B1 --> P["P: ด้านทักษะกระบวนการ (Process/Practice)<br>การปฏิบัติ, ชิ้นงาน, โครงงาน, การทดลอง"]
    B1 --> A1["A: ด้านเจตคติ/คุณลักษณะ (Attitude/Attributes)<br>การเข้าเรียน, ความรับผิดชอบ, วินัย"]
    
    C --> C1["การประเมินรวบยอดปลายภาค (Summative Assessment)<br>เน้นตัวชี้วัดปลายทาง สพฐ."]
```

---

## 🔗 ดัชนีตัวชี้วัด สพฐ. ที่นำมาใช้ในรายวิชาสถานศึกษา (Sample KPI to Course Mapping)
รายวิชาสถานศึกษาเชื่อมโยงเข้ากับตัวชี้วัด สพฐ. ๒๕๖๖ จำนวนมาก ตัวอย่างการแมปปิ้ง:

"""

# Add top 15 sampled mapped KPIs
sampled_kpis = sorted(kpi_to_courses.keys())[:20]
sys_md += "| ตัวชี้วัด สพฐ. | ลิงก์เอกสารแกนกลาง | รายวิชาที่นำไปใช้ | หน่วยการเรียนรู้ที่วัดผล | คะแนนที่วัด |\n"
sys_md += "| :--- | :--- | :--- | :--- | :--- |\n"
for k in sampled_kpis:
    c_entries = kpi_to_courses[k]
    first_c = c_entries[0]
    c_code = first_c['course_code']
    c_name = first_c['course_name']
    u_no = first_c['unit_no']
    u_name = first_c['unit_name']
    score = first_c['total_score']
    kpi_file = k.replace('/', '-')
    sys_md += f"| **{k}** | [[{kpi_file}|วิเคราะห์ตัวชี้วัด]] | `{c_code}` {c_name} | หน่วยที่ {u_no} ({u_name}) | {score} คะแนน |\n"

sys_md += """
*(ดูรายงานความครอบคลุมตัวชี้วัดทั้งหมดได้ในตารางโครงสร้างของแต่ละรายวิชา)*

---

## 🛠️ แนวทางการนำไปประยุกต์ใช้ในระบบ AI และระบบจัดการเรียนการสอน
1. **API & Data Engine:** ข้อมูลแผนวัดทั้งหมดถูกแปลงเป็นโครงสร้าง `school_courses_assessment_matrix.json` พร้อมให้นำไปเชื่อมต่อกับระบบ Web App, ระบบสร้างข้อสอบ (Test Blueprint), และระบบบันทึกคะแนน ปพ.5
2. **Lesson Plan Prompting:** สามารถส่งข้อมูล JSON รายวิชา ให้ AI ช่วยร่างแผนการจัดการเรียนรู้รายชั่วโมง พร้อมเกณฑ์การประเมิน (Rubric Scoring) ตามสัดส่วน K-P-A ของแต่ละหน่วย
"""

with open(sys_hub_path, 'w', encoding='utf-8') as f:
    f.write(sys_md)
print(f"Generated: {sys_hub_path}")

# 2. Generate 00_ดัชนีรายวิชาทั้งหมด.md
all_index_path = os.path.join(vault_base, "00_ดัชนีรายวิชาทั้งหมด.md")
idx_md = f"""---
title: "ดัชนีรายวิชาทั้งหมดในหลักสูตรสถานศึกษา โรงเรียนพัฒนานิคม"
type: "all_courses_index"
total_courses: {len(courses)}
tags: [all_courses, school_curriculum, โรงเรียนพัฒนานิคม]
---

# 📚 ดัชนีรายวิชาทั้งหมด (Course Directory)
### หลักสูตรสถานศึกษา โรงเรียนพัฒนานิคม (พ.ศ. ๒๕๖๙–๒๕๗๑)

> ย้อนกลับ: [[00_หลักสูตรสถานศึกษา]] | [[00_ระบบแผนการวัดและประเมินผล]]

| รหัสวิชา | ชื่อรายวิชา | กลุ่มสาระการเรียนรู้ | ระดับชั้น | หน่วยกิต/เวลา | จำนวนหน่วย | ลิงก์โครงสร้างและแผนวัด |
| :---: | :--- | :--- | :---: | :---: | :---: | :--- |
"""

for code in sorted(courses.keys()):
    c = courses[code]
    name = c.get('course_name', '')
    area = c.get('normalized_area', '')
    grade = c.get('grade_level', '-')
    hrs = c.get('hours', '-')
    cred = c.get('credits', '-')
    u_len = len(c.get('units', []))
    safe_name = re.sub(r'[\\/*?:"<>|]', '', name).strip()[:80]
    fn = f"{code}_{safe_name}" if safe_name else code
    idx_md += f"| `{code}` | **{name}** | {area} | {grade} | {cred} นก. ({hrs} ชม.) | {u_len} หน่วย | [[{fn}|ดูแผนวัด]] |\n"

with open(all_index_path, 'w', encoding='utf-8') as f:
    f.write(idx_md)
print(f"Generated: {all_index_path}")

# 3. Generate Area Hub Files (00_กลุ่มสาระ_{name}.md) in each folder
for folder, name in area_order:
    c_list = area_courses.get(folder, [])
    area_hub_path = os.path.join(vault_base, folder, f"00_กลุ่มสาระ_{name}.md")
    
    a_md = f"""---
title: "กลุ่มสาระการเรียนรู้{name} - หลักสูตรสถานศึกษา"
type: "learning_area_school_hub"
area: "{name}"
total_courses: {len(c_list)}
tags: [school_curriculum, {name}, โรงเรียนพัฒนานิคม]
---

# 📖 กลุ่มสาระการเรียนรู้{name}
### หลักสูตรสถานศึกษา โรงเรียนพัฒนานิคม (พ.ศ. ๒๕๖๙–๒๕๗๑)

> ย้อนกลับ: [[00_หลักสูตรสถานศึกษา]] | [[00_ระบบแผนการวัดและประเมินผล]] | [[00_ดัชนีรายวิชาทั้งหมด]]

---

## 📋 รายวิชาทั้งหมดในกลุ่มสาระฯ ({len(c_list)} รายวิชา)

| รหัสวิชา | ชื่อรายวิชา | ระดับชั้น | ภาคเรียน | หน่วยกิต/ชั่วโมง | หน่วยการเรียนรู้ | ลิงก์โครงสร้างรายวิชาและแผนวัด |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- |
"""
    for c in sorted(c_list, key=lambda x: x.get('course_code', '')):
        code = c.get('course_code', '')
        cname = c.get('course_name', '')
        grade = c.get('grade_level', '-')
        sem = c.get('semester', '-')
        hrs = c.get('hours', '-')
        cred = c.get('credits', '-')
        ulen = len(c.get('units', []))
        safe_name = re.sub(r'[\\/*?:"<>|]', '', cname).strip()[:80]
        fn = f"{code}_{safe_name}" if safe_name else code
        a_md += f"| `{code}` | **{cname}** | {grade} | {sem} | {cred} นก. ({hrs} ชม.) | {ulen} หน่วย | [[{fn}|เปิดแผนวัด {code}]] |\n"

    with open(area_hub_path, 'w', encoding='utf-8') as f:
        f.write(a_md)
    print(f"Generated area hub: {area_hub_path}")

# 4. Update 00_หลักสูตรสถานศึกษา.md
main_hub_path = os.path.join(vault_base, "00_หลักสูตรสถานศึกษา.md")
main_md = f"""---
title: "หลักสูตรสถานศึกษา โรงเรียนพัฒนานิคม"
type: "school_curriculum_hub"
academic_years: "2569–2571"
total_courses: {len(courses)}
tags: [school_curriculum, โรงเรียนพัฒนานิคม, แผนการวัดและประเมินผล]
---

# 🏫 หลักสูตรสถานศึกษา โรงเรียนพัฒนานิคม
### สำนักงานเขตพื้นที่การศึกษามัธยมศึกษาลพบุรี (พ.ศ. ๒๕๖๙ – ๒๕๗๑)

ยินดีต้อนรับสู่คลังข้อมูลดิจิทัลหลักสูตรสถานศึกษา โรงเรียนพัฒนานิคม ระบบนี้ประกอบด้วยข้อมูลโครงสร้างหลักสูตร คำอธิบายรายวิชา และ **ตารางโครงสร้างรายวิชาพร้อมแผนการวัดและประเมินผลการเรียนรู้ (Assessment Matrix Blueprint)** ครบทั้ง 8 กลุ่มสาระการเรียนรู้ รวมทั้งสิ้น **{len(courses)} รายวิชา**

---

## 🌟 จุดเด่นของระบบแผนวัดและหลักสูตรดิจิทัล
1. **ตารางแผนวัดสมบูรณ์แบบ:** ประกอบด้วย หน่วยที่, ชื่อหน่วย, มาตรฐาน/ตัวชี้วัด/ผลการเรียนรู้, สาระสำคัญ, เวลาเรียน, และน้ำหนักคะแนนจำแนกตาม **K (ความรู้), P (ทักษะปฏิบัติ), A (คุณลักษณะ)** ครบทุกวิชา
2. **เชื่อมโยงตัวชี้วัด สพฐ. ๒๕๖๖:** ตัวชี้วัดระหว่างทางและปลายทางเชื่อมต่อโดยตรงไปยังเอกสารวิเคราะห์ตัวชี้วัดแกนกลาง 2,056 ตัวชี้วัด
3. **พร้อมสำหรับระบบแผนวัดและ AI:** ข้อมูลถูกจัดเก็บทั้งในรูปแบบ Markdown สำหรับเปิดดูใน Obsidian และ JSON Schema (`school_courses_assessment_matrix.json`) สำหรับนำไปพัฒนาระบบต่อยอด

---

## 🗂️ ทางลัดสู่ระบบและกลุ่มสาระการเรียนรู้

### 📊 ระบบแผนการวัดและประเมินผล
- 📑 [[00_ระบบแผนการวัดและประเมินผล|ระบบแผนการวัดและประเมินผลการเรียนรู้ (Assessment Hub)]]
- 📑 [[00_ดัชนีรายวิชาทั้งหมด|ดัชนีรายวิชาทั้งหมด {len(courses)} วิชา (Course Directory)]]

### 📚 กลุ่มสาระการเรียนรู้ 8 กลุ่มสาระฯ
1. 🇹🇭 [[00_กลุ่มสาระ_ภาษาไทย|01. กลุ่มสาระการเรียนรู้ภาษาไทย]] ({len(area_courses.get('01_ภาษาไทย', []))} วิชา)
2. 📐 [[00_กลุ่มสาระ_คณิตศาสตร์|02. กลุ่มสาระการเรียนรู้คณิตศาสตร์]] ({len(area_courses.get('02_คณิตศาสตร์', []))} วิชา)
3. 🔬 [[00_กลุ่มสาระ_วิทยาศาสตร์และเทคโนโลยี|03. กลุ่มสาระการเรียนรู้วิทยาศาสตร์และเทคโนโลยี]] ({len(area_courses.get('03_วิทยาศาสตร์และเทคโนโลยี', []))} วิชา)
4. 🌏 [[00_กลุ่มสาระ_สังคมศึกษา ศาสนา และวัฒนธรรม|04. กลุ่มสาระการเรียนรู้สังคมศึกษา ศาสนา และวัฒนธรรม]] ({len(area_courses.get('04_สังคมศึกษา', []))} วิชา)
5. ⚽ [[00_กลุ่มสาระ_สุขศึกษาและพลศึกษา|05. กลุ่มสาระการเรียนรู้สุขศึกษาและพลศึกษา]] ({len(area_courses.get('05_สุขศึกษาและพลศึกษา', []))} วิชา)
6. 🎨 [[00_กลุ่มสาระ_ศิลปะ|06. กลุ่มสาระการเรียนรู้ศิลปะ]] ({len(area_courses.get('06_ศิลปะ', []))} วิชา)
7. 🔨 [[00_กลุ่มสาระ_การงานอาชีพ|07. กลุ่มสาระการเรียนรู้การงานอาชีพ]] ({len(area_courses.get('07_การงานอาชีพ', []))} วิชา)
8. 🌐 [[00_กลุ่มสาระ_ภาษาต่างประเทศ|08. กลุ่มสาระการเรียนรู้ภาษาต่างประเทศ]] ({len(area_courses.get('08_ภาษาต่างประเทศ', []))} วิชา)

---

> 🔗 เชื่อมโยง: [[00_สารบัญหลักสูตรแกนกลาง|กลับสู่คลังหลักสูตรแกนกลาง สพฐ. ๒๕๖๖]]
"""

with open(main_hub_path, 'w', encoding='utf-8') as f:
    f.write(main_md)
print(f"Generated main hub: {main_hub_path}")

