import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

MATRIX_PATH = 'school_courses_assessment_matrix.json'
CATALOG_PATH = 'semester_catalog.json'

print("=== Starting Synchronization of Curriculum Data ===")

# 1. Load Matrix
with open(MATRIX_PATH, 'r', encoding='utf-8') as f:
    matrix = json.load(f)

print(f"Original Matrix courses: {len(matrix)}")

# 2. Delete duplicate/typo courses
to_delete = ['ค2010', 'งง30226']
for code in to_delete:
    if code in matrix:
        del matrix[code]
        print(f"Deleted {code} from matrix")

print(f"Matrix courses after deletion: {len(matrix)}")

# 3. Apply Credit/Hour updates
ch_updates = {
    'ว30221': {'credits': 1.5, 'total_hours': 60, 'target_pre': 29, 'target_post': 29},
    'ว30267': {'credits': 0.5, 'total_hours': 20, 'target_pre': 9, 'target_post': 9},
    'ว30268': {'credits': 0.5, 'total_hours': 20, 'target_pre': 9, 'target_post': 9},
    'ศ32201': {'credits': 1.0, 'total_hours': 40, 'target_pre': 19, 'target_post': 19},
    'ง30222': {'credits': 0.5, 'total_hours': 20, 'target_pre': 9, 'target_post': 9},
    'ง30223': {'credits': 0.5, 'total_hours': 20, 'target_pre': 9, 'target_post': 9},
}

for code, up in ch_updates.items():
    if code in matrix:
        c = matrix[code]
        c['credits'] = up['credits']
        c['total_hours'] = up['total_hours']
        c['target_pre_hours'] = up['target_pre']
        c['target_post_hours'] = up['target_post']
        print(f"Updated credits/hours for {code}: {up['credits']}cr / {up['total_hours']}h")

# Specifically update units for ว30221 to authentic 3 units matching 60 hours
matrix['ว30221']['units'] = [
    {
        "unit_no": "1",
        "unit_name": "ความปลอดภัยและทักษะในปฏิบัติการเคมี",
        "hours": 10,
        "score_k": 10,
        "score_p": 3,
        "score_a": 2,
        "score_total": 15,
        "indicators_raw": [
            "ผลการเรียนรู้ 1", "ผลการเรียนรู้ 2", "ผลการเรียนรู้ 3", "ผลการเรียนรู้ 4"
        ],
        "key_concepts": [
            "ความปลอดภัยในการทำงานกับสารเคมี อุบัติเหตุจากสารเคมี การวัดปริมาณสาร อุปกรณ์วัดปริมาตรและวัดมวล เลขนัยสำคัญ หน่วยวัดในระบบเอสไอ แฟกเตอร์เปลี่ยนหน่วย และวิธีการทางวิทยาศาสตร์"
        ]
    },
    {
        "unit_no": "2",
        "unit_name": "อะตอมและสมบัติของธาตุ",
        "hours": 19,
        "score_k": 10,
        "score_p": 6,
        "score_a": 4,
        "score_total": 20,
        "indicators_raw": [
            "ผลการเรียนรู้ 5", "ผลการเรียนรู้ 6", "ผลการเรียนรู้ 7", "ผลการเรียนรู้ 8-10", "ผลการเรียนรู้ 11-12"
        ],
        "key_concepts": [
            "แบบจำลองอะตอม สัญลักษณ์นิวเคลียร์ ไอโซโทป การจัดเรียงอิเล็กตรอนในอะตอม แนวโน้มสมบัติของธาตุตามหมู่และตามคาบ สมบัติของธาตุแทรนซิชัน การสลายตัวและครึ่งชีวิตของธาตุกัมมันตรังสี"
        ]
    },
    {
        "unit_no": "3",
        "unit_name": "พันธะเคมี",
        "hours": 29,
        "score_k": 20,
        "score_p": 11,
        "score_a": 4,
        "score_total": 35,
        "indicators_raw": [
            "ผลการเรียนรู้ 13-17", "ผลการเรียนรู้ 18-23", "ผลการเรียนรู้ 24-25"
        ],
        "key_concepts": [
            "สัญลักษณ์แบบจุดของลิวอิสและกฎออกเตต พันธะไอออนิก วัฏจักรบอร์น-ฮาเบอร์ สมการไอออนิก พันธะโคเวเลนต์ พลังงานพันธะ รูปร่างและสภาพขั้วโมเลกุล แรงยึดเหนี่ยวระหว่างโมเลกุล พันธะโลหะ และการนำสารประกอบไปใช้ประโยชน์"
        ]
    }
]

# Adjust units for 20h courses (ว30267, ว30268, ง30222, ง30223)
for code in ['ว30267', 'ว30268', 'ง30222', 'ง30223']:
    if code in matrix:
        units = matrix[code].get('units', [])
        if len(units) >= 4:
            units[0]['hours'] = 4
            units[1]['hours'] = 5
            units[2]['hours'] = 4
            units[3]['hours'] = 5
        elif len(units) == 2:
            units[0]['hours'] = 9
            units[1]['hours'] = 9

# Adjust units for ศ32201 (40h)
if 'ศ32201' in matrix:
    units = matrix['ศ32201'].get('units', [])
    if len(units) >= 4:
        units[0]['hours'] = 9
        units[1]['hours'] = 10
        units[2]['hours'] = 9
        units[3]['hours'] = 10

# 4. Apply Course Name updates (31 courses)
name_updates = {
    'ท30201': 'ภาษาไทยเพื่อกิจกรรมการแสดง 1',
    'ท30202': 'ภาษาไทยเพื่อกิจกรรมการแสดง 2',
    'ท31101': 'ภาษาไทย 1',
    'ท31201': 'การเขียน 1',
    'ท31203': 'การเขียน 2',
    'ท32203': 'ประวัติวรรณคดี 1',
    'ท32204': 'ประวัติวรรณคดี 2',
    'ท33201': 'ภาษาไทยเพื่อการศึกษาต่อ 1',
    'ท33203': 'ภาษาไทยเพื่อการศึกษาต่อ 2',
    'ค31203': 'คณิตศาสตร์อุตสาหกรรม 1',
    'ค31204': 'คณิตศาสตร์อุตสาหกรรม 2',
    'ค33204': 'คณิตศาสตร์อุตสาหกรรม 6',
    'ว20224': 'Google SketchUp (Model 3D)',
    'ว30287': 'คอมพิวเตอร์กราฟิก 1',
    'ว30288': 'คอมพิวเตอร์กราฟิก 2',
    'ว30289': 'การเขียนโปรแกรมเบื้องต้น 1',
    'ว30290': 'การเขียนโปรแกรมเบื้องต้น 2',
    'พ21102': 'พลศึกษา 1',
    'พ21104': 'พลศึกษา 2',
    'พ22101': 'สุขศึกษาและพลศึกษา 3',
    'พ22102': 'พลศึกษา 3',
    'พ22104': 'พลศึกษา 4',
    'พ23101': 'สุขศึกษาและพลศึกษา 5',
    'พ23102': 'พลศึกษา 5',
    'พ23104': 'พลศึกษา 6',
    'ศ22101': 'ศิลปะพื้นฐาน 3',
    'ศ23102': 'ศิลปะพื้นฐาน 6',
    'ง21102': 'การงานอาชีพ 1',
    'อ20228': 'ภาษาอังกฤษเพื่อการเข้าสังคม 1',
    'ช2551': 'กิจกรรมแนะแนว',
    'ช2560': 'กิจกรรมแนะแนว'
}

for code, new_name in name_updates.items():
    if code in matrix:
        old_name = matrix[code].get('course_name')
        matrix[code]['course_name'] = new_name
        print(f"Renamed {code}: '{old_name}' -> '{new_name}'")

# Save Matrix
with open(MATRIX_PATH, 'w', encoding='utf-8') as f:
    json.dump(matrix, f, ensure_ascii=False, indent=2)
print(f"Saved {MATRIX_PATH} with {len(matrix)} courses.")

# 5. Update semester_catalog.json
with open(CATALOG_PATH, 'r', encoding='utf-8') as f:
    catalog = json.load(f)

by_code = catalog.get('by_course_code', {})
# Delete duplicate codes
for code in to_delete:
    if code in by_code:
        del by_code[code]
        print(f"Deleted {code} from semester_catalog by_course_code")

# Update credits/hours and names in by_code
for code, up in ch_updates.items():
    if code in by_code:
        by_code[code]['credits'] = up['credits']
        by_code[code]['total_hours'] = up['total_hours']

for code, new_name in name_updates.items():
    if code in by_code:
        by_code[code]['course_name'] = new_name

# Clean by_semester
by_sem = catalog.get('by_semester', {})
for sem, groups in by_sem.items():
    if isinstance(groups, dict):
        for grp_key in list(groups.keys()):
            items = groups[grp_key]
            if isinstance(items, list):
                # Filter out to_delete
                filtered = []
                for item in items:
                    if isinstance(item, dict):
                        icode = item.get('code')
                        if icode in to_delete:
                            print(f"Removed {icode} from by_semester[{sem}][{grp_key}]")
                            continue
                        # Update name/credits/hours if in item
                        if icode in name_updates:
                            item['name'] = name_updates[icode]
                        if icode in ch_updates:
                            item['credits'] = ch_updates[icode]['credits']
                            item['hours'] = ch_updates[icode]['total_hours']
                    filtered.append(item)
                groups[grp_key] = filtered

# Update metadata
if 'metadata' not in catalog:
    catalog['metadata'] = {}
catalog['metadata']['total_courses'] = len(by_code)
catalog['metadata']['verified_courses'] = len(by_code)

with open(CATALOG_PATH, 'w', encoding='utf-8') as f:
    json.dump(catalog, f, ensure_ascii=False, indent=2)
print(f"Saved {CATALOG_PATH} with {len(by_code)} courses.")

print("=== Synchronization Complete ===")
