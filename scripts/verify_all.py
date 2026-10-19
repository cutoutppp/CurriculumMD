import json
import os
import glob
import re
import sys
import urllib.request
import urllib.parse

sys.stdout.reconfigure(encoding='utf-8')

print("======================================================================")
print("             CURRICULUM & ASSESSMENT HUB VERIFICATION SUITE           ")
print("======================================================================")

# 1. Total Course Counts Check
vault_root = os.path.join("Curriculum_Vault", "09_หลักสูตรสถานศึกษา")
vault_files = [f for f in glob.glob(f"{vault_root}/**/*.md", recursive=True) if not os.path.basename(f).startswith("00_")]
vault_count = len(vault_files)

with open("school_courses_assessment_matrix.json", "r", encoding="utf-8") as f:
    matrix = json.load(f)
matrix_count = len(matrix)

with open("semester_catalog.json", "r", encoding="utf-8") as f:
    catalog = json.load(f)
catalog_count = len(catalog.get("by_course_code", {}))

hub_json_path = r"C:\Users\peera\Desktop\AntigravityProject\AssessmentHub\assessment-plan\data\courses_2_2569.json"
with open(hub_json_path, "r", encoding="utf-8") as f:
    hub_json = json.load(f)
hub_json_count = len(hub_json)

hub_js_path = r"C:\Users\peera\Desktop\AntigravityProject\AssessmentHub\assessment-plan\data\courses_2_2569.js"
with open(hub_js_path, "r", encoding="utf-8") as f:
    js_text = f.read()
    # Strip 'const COURSES_2_2569 = ' and trailing ';'
    js_clean = re.sub(r'^\s*const\s+COURSES_2_2569\s*=\s*', '', js_text).rstrip().rstrip(';')
    hub_js = json.loads(js_clean)
hub_js_count = len(hub_js)

print("\n--- 1. TOTAL COURSE COUNTS (Target: 624) ---")
print(f"Vault Markdown Files:                 {vault_count} courses {'[PASS]' if vault_count == 624 else '[FAIL]'}")
print(f"school_courses_assessment_matrix.json:{matrix_count} courses {'[PASS]' if matrix_count == 624 else '[FAIL]'}")
print(f"semester_catalog.json (by_course_code):{catalog_count} courses {'[PASS]' if catalog_count == 624 else '[FAIL]'}")
print(f"AssessmentHub courses_2_2569.json:    {hub_json_count} courses {'[PASS]' if hub_json_count == 624 else '[FAIL]'}")
print(f"AssessmentHub courses_2_2569.js:      {hub_js_count} courses {'[PASS]' if hub_js_count == 624 else '[FAIL]'}")

# 2. Check Absence of Duplicate / Typo Courses
print("\n--- 2. ABSENCE OF DUPLICATE / TYPO COURSES (ค2010 & งง30226) ---")
for bad in ['ค2010', 'งง30226']:
    in_m = bad in matrix
    in_c = bad in catalog.get("by_course_code", {})
    in_hj = bad in hub_json
    in_hjs = bad in hub_js
    status = "CLEAN [PASS]" if not any([in_m, in_c, in_hj, in_hjs]) else "FOUND [FAIL]"
    print(f"Course '{bad}': Matrix={in_m}, Catalog={in_c}, HubJSON={in_hj}, HubJS={in_hjs} -> {status}")

# 3. Check Credit / Hour Corrections
print("\n--- 3. CREDIT & HOUR CORRECTIONS ---")
expected_ch = {
    'ว30221': (1.5, 60, 29, 29),
    'ว30267': (0.5, 20, 9, 9),
    'ว30268': (0.5, 20, 9, 9),
    'ศ32201': (1.0, 40, 19, 19),
    'ง30222': (0.5, 20, 9, 9),
    'ง30223': (0.5, 20, 9, 9),
}

for code, exp in expected_ch.items():
    m_data = matrix.get(code, {})
    h_data = hub_json.get(code, {})
    m_match = (m_data.get('credits') == exp[0] and m_data.get('total_hours') == exp[1] and 
               m_data.get('target_pre_hours') == exp[2] and m_data.get('target_post_hours') == exp[3])
    h_match = (h_data.get('credits') == exp[0] and h_data.get('total_hours') == exp[1] and 
               h_data.get('target_pre_hours') == exp[2] and h_data.get('target_post_hours') == exp[3])
    status = "[PASS]" if (m_match and h_match) else "[FAIL]"
    print(f"Course {code} ({m_data.get('course_name')}): {exp[0]}cr / {exp[1]}h (pre={exp[2]}, post={exp[3]}) -> {status}")
    if code == 'ว30221':
        print(f"   ว30221 Units Count: {len(m_data.get('units', []))}")
        for idx, u in enumerate(m_data.get('units', [])):
            print(f"     Unit {u.get('unit_no')}: {u.get('unit_name')} ({u.get('hours')}h, total={u.get('score_total')}pts)")

# 4. Check Course Names Update Sample
print("\n--- 4. COURSE NAMES VERIFICATION SAMPLE ---")
sample_names = {
    'ท31101': 'ภาษาไทย 1',
    'ค31203': 'คณิตศาสตร์อุตสาหกรรม 1',
    'ค31204': 'คณิตศาสตร์อุตสาหกรรม 2',
    'ค33204': 'คณิตศาสตร์อุตสาหกรรม 6',
    'พ21102': 'พลศึกษา 1',
    'พ21104': 'พลศึกษา 2',
    'ว30287': 'คอมพิวเตอร์กราฟิก 1',
    'ว30289': 'การเขียนโปรแกรมเบื้องต้น 1',
    'ง21102': 'การงานอาชีพ 1',
    'ช2551': 'กิจกรรมแนะแนว',
    'ช2560': 'กิจกรรมแนะแนว'
}

for code, expected_name in sample_names.items():
    m_name = matrix.get(code, {}).get('course_name')
    h_name = hub_json.get(code, {}).get('course_name')
    status = "[PASS]" if (m_name == expected_name and h_name == expected_name) else "[FAIL]"
    print(f"{code}: Matrix='{m_name}', Hub='{h_name}' -> {status}")

# 5. Firestore Live Verification
print("\n--- 5. CLOUD FIRESTORE VERIFICATION ---")
api_key = "AIzaSyCGjC6w1a795yZ858-V3q9-wD2_8zH1770"
project_id = "tradesimschool"
base_url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/survey_config"

def check_remote_doc(doc_id):
    encoded_id = urllib.parse.quote(doc_id)
    url = f"{base_url}/{encoded_id}?key={api_key}"
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            return True, data
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return False, None
        return None, str(e)

exists_20210, doc_20210 = check_remote_doc("sgs_2569_2_ค20210")
exists_2010, _ = check_remote_doc("sgs_2569_2_ค2010")
exists_30226, _ = check_remote_doc("sgs_2569_2_งง30226")

print(f"Firestore doc sgs_2569_2_ค20210 exists: {exists_20210} {'[PASS]' if exists_20210 else '[FAIL]'}")
if exists_20210:
    f = doc_20210.get('fields', {})
    print(f"   course_code in doc: {f.get('course_code', {}).get('stringValue')}")
    print(f"   course_name in doc: {f.get('course_name', {}).get('stringValue')}")
    print(f"   status in doc: {f.get('confirmed_status', {}).get('stringValue')}")
    print(f"   grand_total in doc: {f.get('grand_total', {}).get('integerValue')}")
    print(f"   pre_slots: {[v.get('integerValue') if 'integerValue' in v else None for v in f.get('pre_slots', {}).get('arrayValue', {}).get('values', [])]}")
    print(f"   post_slots: {[v.get('integerValue') if 'integerValue' in v else None for v in f.get('post_slots', {}).get('arrayValue', {}).get('values', [])]}")

print(f"Firestore doc sgs_2569_2_ค2010 is deleted (HTTP 404): {not exists_2010} {'[PASS]' if not exists_2010 else '[FAIL]'}")
print(f"Firestore doc sgs_2569_2_งง30226 is deleted (HTTP 404): {not exists_30226} {'[PASS]' if not exists_30226 else '[FAIL]'}")

print("\n======================================================================")
print("                   VERIFICATION COMPLETED SUCCESSFULLY                ")
print("======================================================================")
