# -*- coding: utf-8 -*-
import json

with open('kpi_data.js', 'r', encoding='utf-8') as f:
    content = f.read()

raw_json = content[content.find('{'):content.rfind('}')+1]
data = json.loads(raw_json)
kpis = data.get('kpis', [])
soc_kpis = [k for k in kpis if k.get('subject') == 'สังคมศึกษา ศาสนา และวัฒนธรรม']

with open('semester_catalog.json', 'r', encoding='utf-8') as f:
    cat = json.load(f)

by_code = cat.get('by_course_code', {})
soc_courses = {k: v for k, v in by_code.items() if k.startswith('ส')}

out = []
out.append(f"Social courses in semester_catalog: {len(soc_courses)}")
for k, v in sorted(soc_courses.items()):
    out.append(f"  {k} ({v.get('name')} | {v.get('grade')} เทอม {v.get('term')}): {len(v.get('kpis', []))} KPIs")

# Check all KPIs referenced across these courses
kpis_in_catalog = set()
for c_code, c_info in soc_courses.items():
    for k_code in c_info.get('kpis', []):
        kpis_in_catalog.add(k_code)

out.append(f"\nUnique Social Studies KPIs referenced in semester_catalog: {len(kpis_in_catalog)}")

# Find which secondary social studies KPIs are in kpi_data.js vs semester_catalog.json
sec_soc_kpis = [k for k in soc_kpis if 'ม.' in str(k.get('grade'))]
out.append(f"Total secondary Social Studies KPIs in core curriculum: {len(sec_soc_kpis)}")

missing_in_catalog = []
for k in sec_soc_kpis:
    code = k.get('code')
    if code not in kpis_in_catalog:
        missing_in_catalog.append(k)

out.append(f"Secondary Social Studies KPIs NOT in semester_catalog: {len(missing_in_catalog)}")
for k in missing_in_catalog:
    out.append(f"  - {k.get('code')} ({k.get('grade')} | {k.get('standard')}): {k.get('text')}")

with open('soc_catalog_comparison.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))

print("Catalog comparison completed.")
