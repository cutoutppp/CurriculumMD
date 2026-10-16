import json
import os
import re

with open('kpi_data.js', 'r', encoding='utf-8') as f:
    content = f.read()
prefix = 'const OPEN_CURRICULUM_DATA = '
idx = content.find(prefix)
data = json.loads(content[idx + len(prefix):].rstrip().rstrip(';'))

with open('remaining_unmapped_kpis.json', 'w', encoding='utf-8') as out:
    result = {}
    for subj in [
        'การงานอาชีพ', 'คณิตศาสตร์', 'ภาษาต่างประเทศ', 
        'ภาษาไทย', 'วิทยาศาสตร์และเทคโนโลยี', 'ศิลปะ', 'สุขศึกษาและพลศึกษา'
    ]:
        kpis = [k for k in data['kpis'] if k.get('subject') == subj]
        sec_kpis = [k for k in kpis if any(('ม.' + str(i)) in k.get('grade', '') or 'ม.4-6' in k.get('grade', '') for i in range(1, 7))]
        unmapped = [k for k in sec_kpis if len(k.get('courses', [])) == 0]
        mapped = [k for k in sec_kpis if len(k.get('courses', [])) > 0]
        result[subj] = {
            'total_secondary': len(sec_kpis),
            'mapped': len(mapped),
            'unmapped_count': len(unmapped),
            'unmapped_codes': [k['code'] for k in unmapped]
        }
    json.dump(result, out, ensure_ascii=False, indent=2)

print("remaining_unmapped_kpis.json generated successfully")
