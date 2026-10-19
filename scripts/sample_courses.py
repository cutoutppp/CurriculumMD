import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('school_courses_assessment_matrix.json', 'r', encoding='utf-8') as f:
    matrix = json.load(f)

for code, c in matrix.items():
    if c.get('credits') == 1.5 and c.get('total_hours') == 60:
        print(f"Sample 1.5cr: {code} ({c.get('course_name')}) target_pre={c.get('target_pre_hours')}, target_post={c.get('target_post_hours')}")
        print("  units:", [(u.get('unit_no'), u.get('hours'), u.get('score_total')) for u in c.get('units', [])])
        break

for code, c in matrix.items():
    if c.get('credits') == 0.5 and c.get('total_hours') == 20:
        print(f"Sample 0.5cr: {code} ({c.get('course_name')}) target_pre={c.get('target_pre_hours')}, target_post={c.get('target_post_hours')}")
        print("  units:", [(u.get('unit_no'), u.get('hours'), u.get('score_total')) for u in c.get('units', [])])
        break

for code, c in matrix.items():
    if c.get('credits') == 1.0 and c.get('total_hours') == 40:
        print(f"Sample 1.0cr: {code} ({c.get('course_name')}) target_pre={c.get('target_pre_hours')}, target_post={c.get('target_post_hours')}")
        print("  units:", [(u.get('unit_no'), u.get('hours'), u.get('score_total')) for u in c.get('units', [])])
        break
