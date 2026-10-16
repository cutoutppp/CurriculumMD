# -*- coding: utf-8 -*-
import json

with open('kpi_data.js', 'r', encoding='utf-8') as f:
    text = f.read()

prefix = '/* Generated for Thailand Open Curriculum Portal */\nconst OPEN_CURRICULUM_DATA = '
if text.startswith(prefix):
    json_text = text[len(prefix):].rstrip().rstrip(';')
else:
    idx = text.find('{')
    json_text = text[idx:].rstrip().rstrip(';')

data = json.loads(json_text)

print("=" * 80)
print("VERIFICATION OF SECONDARY KPI MAPPING (ม.1 - ม.6) ACROSS ALL 8 SUBJECTS")
print("=" * 80)

subjects = [
    'ภาษาไทย', 'คณิตศาสตร์', 'วิทยาศาสตร์และเทคโนโลยี', 
    'สังคมศึกษา ศาสนา และวัฒนธรรม', 'สุขศึกษาและพลศึกษา', 
    'ศิลปะ', 'การงานอาชีพ', 'ภาษาต่างประเทศ'
]

all_passed = True
total_sec_core = 0
total_sec_offered = 0

for s in subjects:
    kpis = [k for k in data['kpis'] if k['subject'] == s]
    sec_kpis = [k for k in kpis if any(f'ม.{i}' in k['grade'] or 'ม.4-6' in k['grade'] for i in range(1, 7))]
    sec_offered = [k for k in sec_kpis if len(k.get('courses', [])) > 0]
    
    total_sec_core += len(sec_kpis)
    total_sec_offered += len(sec_offered)
    
    diff = len(sec_kpis) - len(sec_offered)
    status = "PASS (100.0%)" if diff == 0 else f"FAIL (-{diff})"
    if diff != 0:
        all_passed = False
        
    print(f"กลุ่มสาระฯ {s:<28}: ทั้งหมด {len(sec_kpis):3d} ข้อ | เปิดสอน {len(sec_offered):3d} ข้อ | ผล: {status}")

print("-" * 80)
print(f"สรุปยอดรวม มัธยมศึกษา (ม.1 - ม.6):")
print(f"  - ตัวชี้วัดตามหลักสูตรแกนกลาง : {total_sec_core} ตัวชี้วัด")
print(f"  - ตัวชี้วัดที่โรงเรียนเปิดสอน   : {total_sec_offered} ตัวชี้วัด")
print(f"  - ความสอดคล้อง (Fidelity Rate) : {total_sec_offered / total_sec_core * 100:.2f}%")
print("=" * 80)

if all_passed and total_sec_core == 995 and total_sec_offered == 995:
    print(">>> SUCCESS: ทุกวิชา ม.1 - ม.6 มีตัวชี้วัดครบถ้วน 100.0% เท่ากันทุกระบบ <<<")
else:
    print(">>> ERROR: ยังมีความไม่เท่ากัน <<<")
