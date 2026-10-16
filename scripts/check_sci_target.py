import json

with open('kpi_data.js', 'r', encoding='utf-8') as f:
    c = f.read()
data = json.loads(c[c.find('const OPEN_CURRICULUM_DATA = ') + 29:].rstrip().rstrip(';'))

target_codes = [
    'ว 1.2 ม.4/1', 'ว 1.2 ม.4/2', 'ว 1.2 ม.4/3', 'ว 1.2 ม.4/4',
    'ว 1.3 ม.4/1', 'ว 1.3 ม.4/2', 'ว 1.3 ม.4/3', 'ว 1.3 ม.4/4', 'ว 1.3 ม.4/5', 'ว 1.3 ม.4/6'
]

for k in data['kpis']:
    if k['code'] in target_codes:
        print(f"{k['code']} ({k['type']}): {k['text']}")
