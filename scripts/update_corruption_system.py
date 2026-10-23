import json
import os
import glob
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("======================================================================")
print("     UPDATING ANTI-CORRUPTION EDUCATION ASSESSMENT PLAN SYSTEM        ")
print("======================================================================")

TEACHERS_CORRUPTION = [
    "นางสาวณรัณทร กรภัทร์พร",
    "นางเมธาวี วัฒนวงศ์",
    "นางสกาวรัตน์ หนูสลุง",
    "นายปารเมศ มหิเมือง",
    "นางอรทัย กองปัญญา",
    "นางกาญจนา พันธุรักษ์",
    "นายฉัฐพิพัฒน์ สืบเพ็ง",
    "นางสาวพรปวีณ์ แขวนสันเทียะ",
    "นางสาวศิรดา ศรีวิลักษณ์",
    "นายนิติพงษ์ คำนะ",
    "นางเรวดี กวางโตน",
    "นายจักรกฤษณ์ โพธิ์ภาสี",
    "นางสาวอัจฉรา จันทร์ผ่อง",
    "นายนนทกานต์ พรมมา",
    "นางนันทิดา พิมพ์สมบูรณ์",
    "นายวายุ ก้งทอง",
    "นายพงศธร แสนเมือง",
    "นางสาวชิดชนก พยัคฆโส",
    "นายอิฐสรา บุญคล้าย",
    "นางสาวสุนันทณี ขุนทอง"
]

INDICATORS_CORRUPTION = [
    "1. มีความรู้ ความเข้าใจเกี่ยวกับ STRONG : จิตพอเพียงต้านทุจริต",
    "2. ปฏิบัติตนเป็นผู้ที่ STRONG : จิตพอเพียงต้านทุจริต",
    "3. มีความรู้ ความเข้าใจเกี่ยวกับพลเมืองกับความรับผิดชอบต่อสังคม",
    "4. ปฏิบัติตนตามหน้าที่พลเมืองและมีความรับผิดชอบต่อสังคม",
    "5. ตระหนักและเห็นความสำคัญของการต่อต้านและป้องกันการทุจริต"
]

UNITS_CORRUPTION = [
    {
        "unit_no": "1",
        "unit_name": "STRONG / จิตพอเพียงต้านทุจริต",
        "hours": 5,
        "score_k": 20,
        "score_p": 0,
        "score_a": 0,
        "score_total": 20,
        "indicators_raw": [
            "ข้อที่ 1-2"
        ],
        "eval_method": "- การสังเกตพฤติกรรม\n- การถาม - ตอบ ในชั้นเรียน\n- แบบทดสอบก่อนเรียน-หลังเรียน",
        "key_concepts": [
            "STRONG : จิตพอเพียงต้านทุจริต การสร้างจิตสำนึกและปฏิบัติตนตามหลักความพอเพียงในการต่อต้านการทุจริต"
        ]
    },
    {
        "unit_no": "2",
        "unit_name": "พลเมืองกับความรับผิดชอบต่อสังคม",
        "hours": 4,
        "score_k": 20,
        "score_p": 0,
        "score_a": 0,
        "score_total": 20,
        "indicators_raw": [
            "ข้อที่ 3-4"
        ],
        "eval_method": "- การสังเกตพฤติกรรม\n- การถาม - ตอบ ในชั้นเรียน\n- แบบทดสอบก่อนเรียน-หลังเรียน",
        "key_concepts": [
            "พลเมืองกับความรับผิดชอบต่อสังคม การปฏิบัติตนตามหน้าที่พลเมืองที่ดีและการมีส่วนร่วมรับผิดชอบต่อสังคม"
        ]
    },
    {
        "unit_no": "3",
        "unit_name": "ความสำคัญของการต่อต้านและป้องกันการทุจริต",
        "hours": 4,
        "score_k": 20,
        "score_p": 0,
        "score_a": 0,
        "score_total": 20,
        "indicators_raw": [
            "ข้อที่ 5"
        ],
        "eval_method": "- การสังเกตพฤติกรรม\n- การถาม - ตอบ ในชั้นเรียน\n- แบบทดสอบก่อนเรียน-หลังเรียน",
        "key_concepts": [
            "ความสำคัญของการต่อต้านและป้องกันการทุจริต การสร้างความตระหนักรู้และเห็นคุณค่าของการไม่ทุจริต"
        ]
    },
    {
        "unit_no": "4",
        "unit_name": "บูรณาการความรู้ สู่การป้องกันการทุจริต",
        "hours": 5,
        "score_k": 20,
        "score_p": 0,
        "score_a": 0,
        "score_total": 20,
        "indicators_raw": [
            "ข้อที่ 1-5"
        ],
        "eval_method": "- การสังเกตพฤติกรรม\n- การถาม - ตอบ ในชั้นเรียน\n- แบบทดสอบก่อนเรียน-หลังเรียน",
        "key_concepts": [
            "บูรณาการความรู้สู่การป้องกันการทุจริต การประยุกต์ใช้องค์ความรู้และทักษะเพื่อสร้างสรรค์แนวทางการป้องกันการทุจริตในชีวิตจริง"
        ]
    }
]

# 1. Update semester2_teachers_mapping.json
mapping_file = 'semester2_teachers_mapping.json'
if os.path.exists(mapping_file):
    with open(mapping_file, 'r', encoding='utf-8') as f:
        mapping = json.load(f)
else:
    mapping = {}

term2_corruption_codes = ['ส20224', 'ส20226', 'ส20228', 'ส30248', 'ส30250', 'ส30252']
for code in term2_corruption_codes:
    mapping[code] = {
        "course_code": code,
        "course_name": f"การป้องกันการทุจริต {code[-1]}",
        "learning_area": "สังคมศึกษา ศาสนา และวัฒนธรรม",
        "teachers": TEACHERS_CORRUPTION,
        "grades": ["ม." + ("1" if code=="ส20224" else "2" if code=="ส20226" else "3" if code=="ส20228" else "4" if code=="ส30248" else "5" if code=="ส30250" else "6")],
        "hours_per_week": 1.0
    }
    print(f"Added/Updated teachers mapping for {code}: {len(TEACHERS_CORRUPTION)} teachers")

with open(mapping_file, 'w', encoding='utf-8') as f:
    json.dump(mapping, f, ensure_ascii=False, indent=2)
print("Saved semester2_teachers_mapping.json")

# 2. Update school_courses_assessment_matrix.json
matrix_file = 'school_courses_assessment_matrix.json'
with open(matrix_file, 'r', encoding='utf-8') as f:
    matrix = json.load(f)

all_corruption_codes = [
    'ส20223', 'ส20224', 'ส20225', 'ส20226', 'ส20227', 'ส20228',
    'ส30247', 'ส30248', 'ส30249', 'ส30250', 'ส30251', 'ส30252'
]

for code in all_corruption_codes:
    if code in matrix:
        c = matrix[code]
        c['teachers'] = TEACHERS_CORRUPTION
        c['indicators'] = INDICATORS_CORRUPTION
        c['units'] = UNITS_CORRUPTION
        c['score_ratio'] = "80:20"
        c['ratio_display'] = "80:20 (40:10:40:10)"
        c['kpa_ratio'] = "100:-:-"
        c['score_pre_mid'] = 40
        c['score_mid'] = 10
        c['score_post_mid'] = 40
        c['score_final'] = 10
        c['target_mid_score'] = 10
        c['target_fin_score'] = 10
        c['midExamScores'] = [5, 5]
        c['finExamScores'] = [5, 5]
        c['target_pre_hours'] = 9
        c['target_post_hours'] = 9
        c['total_hours'] = 20
        c['credits'] = 0.5
        c['exam_schedule'] = "สอบนอกตาราง"
        c['exam_duration_text'] = "สอบนอกตาราง"
        c['key_task'] = "-"
        print(f"Updated matrix for {code}: 80:20 ratio, 4 units, K:100, 20 teachers, exam: สอบนอกตาราง")

with open(matrix_file, 'w', encoding='utf-8') as f:
    json.dump(matrix, f, ensure_ascii=False, indent=2)
print(f"Saved {matrix_file}")

# 3. Update Curriculum_Vault Markdown files
vault_dir = r"Curriculum_Vault/09_หลักสูตรสถานศึกษา/04_สังคมศึกษา"
for code in all_corruption_codes:
    pattern = os.path.join(vault_dir, f"{code}_*.md")
    matched = glob.glob(pattern)
    if not matched:
        continue
    md_path = matched[0]
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Build updated table and sections
    table_replacement = """## 🎯 ตารางโครงสร้างรายวิชาและแผนการวัดและประเมินผลการเรียนรู้

อัตราส่วนการประเมินคะแนน: **80 : 20** (ระหว่างภาค : กลางภาค : ปลายภาค = **80 : 10 : 10**, K:P:A = **100 : - : -**)  
เวลาในการสอบ: **สอบนอกตาราง**

| หน่วยที่ | ชื่อหน่วยการเรียนรู้ (จำนวนชั่วโมง) | ผลการเรียนรู้ | วิธีการประเมินผล | K | P | A | รวม |
| :---: | :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| **1. การวัดผลก่อนสอบกลางภาค** | | | | | | | |
| 1 | **STRONG / จิตพอเพียงต้านทุจริต** (5 ชั่วโมง) | ข้อที่ 1-2 | - การสังเกตพฤติกรรม<br>- การถาม - ตอบ ในชั้นเรียน<br>- แบบทดสอบก่อนเรียน-หลังเรียน | 20 | - | - | **20** |
| 2 | **พลเมืองกับความรับผิดชอบต่อสังคม** (4 ชั่วโมง) | ข้อที่ 3-4 | - การสังเกตพฤติกรรม<br>- การถาม - ตอบ ในชั้นเรียน<br>- แบบทดสอบก่อนเรียน-หลังเรียน | 20 | - | - | **20** |
| **รวมคะแนนการวัดผลก่อนสอบกลางภาค** | | | | **40** | **-** | **-** | **40** |
| **2. การวัดผลกลางภาค** | | | | | | | |
| 1 | **STRONG / จิตพอเพียงต้านทุจริต** | ข้อที่ 1-2 | - แบบทดสอบวัดผลกลางภาคเรียน | 5 | - | - | **10** |
| 2 | **พลเมืองกับความรับผิดชอบต่อสังคม** (1 ชั่วโมง) | ข้อที่ 3-4 | | 5 | - | - | |
| **รวมคะแนนการวัดผลกลางภาค** | | | | **10** | **-** | **-** | **10** |
| **3. การวัดผลหลังสอบกลางภาค** | | | | | | | |
| 3 | **ความสำคัญของการต่อต้านและป้องกันการทุจริต** (4 ชั่วโมง) | ข้อที่ 5 | - การสังเกตพฤติกรรม<br>- การถาม - ตอบ ในชั้นเรียน<br>- แบบทดสอบก่อนเรียน-หลังเรียน | 20 | - | - | **20** |
| 4 | **บูรณาการความรู้ สู่การป้องกันการทุจริต** (5 ชั่วโมง) | ข้อที่ 1-5 | - การสังเกตพฤติกรรม<br>- การถาม - ตอบ ในชั้นเรียน<br>- แบบทดสอบก่อนเรียน-หลังเรียน | 20 | - | - | **20** |
| **รวมคะแนนการวัดผลหลังสอบกลางภาค** | | | | **40** | **-** | **-** | **40** |
| **4. การวัดผลปลายภาค** | | | | | | | |
| 3 | **ความสำคัญของการต่อต้านและป้องกันการทุจริต** | ข้อที่ 5 | - แบบทดสอบวัดผลปลายภาคเรียน | 5 | - | - | **10** |
| 4 | **บูรณาการความรู้ สู่การป้องกันการทุจริต** (1 ชั่วโมง) | ข้อที่ 1-5 | | 5 | - | - | |
| **รวมคะแนนการวัดผลปลายภาค** | | | | **10** | **-** | **-** | **10** |
| **รวมคะแนนทั้งหมด** | | | | **100** | **-** | **-** | **100** |

---

## 📋 รายละเอียดตัวชี้วัดและภาระงานประเมิน (Blueprint สำหรับจัดทำแผนการสอนและแผนวัด)

### หน่วยที่ 1: STRONG / จิตพอเพียงต้านทุจริต
- **เวลาเรียน:** 5 ชั่วโมง | **คะแนนรวม:** 20 คะแนน (K: 20 / P: - / A: -)
- **ผลการเรียนรู้:** ข้อที่ 1-2

### หน่วยที่ 2: พลเมืองกับความรับผิดชอบต่อสังคม
- **เวลาเรียน:** 4 ชั่วโมง | **คะแนนรวม:** 20 คะแนน (K: 20 / P: - / A: -)
- **ผลการเรียนรู้:** ข้อที่ 3-4

### หน่วยที่ 3: ความสำคัญของการต่อต้านและป้องกันการทุจริต
- **เวลาเรียน:** 4 ชั่วโมง | **คะแนนรวม:** 20 คะแนน (K: 20 / P: - / A: -)
- **ผลการเรียนรู้:** ข้อที่ 5

### หน่วยที่ 4: บูรณาการความรู้ สู่การป้องกันการทุจริต
- **เวลาเรียน:** 5 ชั่วโมง | **คะแนนรวม:** 20 คะแนน (K: 20 / P: - / A: -)
- **ผลการเรียนรู้:** ข้อที่ 1-5
- **ชิ้นงานสำคัญติด ร:** - (ไม่มี)
"""

    # Replace from "## 🎯 ตารางโครงสร้างรายวิชา" to before "--- \n*ที่มาของข้อมูล" or end
    m_split = re.split(r'##\s*🎯\s*ตารางโครงสร้างรายวิชา', content)
    if len(m_split) == 2:
        pre_part = m_split[0]
        # Check if footer exists
        footer = ""
        m_footer = re.search(r'(\n---\s*\n\*ที่มาของข้อมูล[\s\S]*$)', content)
        if m_footer:
            footer = m_footer.group(1)
        else:
            footer = "\n\n---\n*ที่มาของข้อมูล: แผนการวัดและประเมินผลการเรียนรู้ รายวิชาการป้องกันการทุจริต โรงเรียนพัฒนานิคม พ.ศ. 2569–2571*\n"
        
        new_md = pre_part.rstrip() + "\n\n" + table_replacement.strip() + footer
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(new_md)
        print(f"Updated vault note: {os.path.basename(md_path)}")

print("=== Core Data Updated Successfully ===")
