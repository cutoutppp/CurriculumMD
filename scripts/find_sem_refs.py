import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('semester_catalog.json', 'r', encoding='utf-8') as f:
    sc = json.load(f)

by_sem = sc.get('by_semester', {})
print("by_semester keys:", list(by_sem.keys()))
for sem, content in by_sem.items():
    if isinstance(content, dict):
        for k, v in content.items():
            if isinstance(v, list):
                for item in v:
                    code = item.get('code') if isinstance(item, dict) else str(item)
                    if code in ['ค2010', 'งง30226']:
                        print(f"Found {code} in {sem} -> {k}")
            elif isinstance(v, dict):
                for k2, v2 in v.items():
                    if isinstance(v2, list):
                        for item in v2:
                            code = item.get('code') if isinstance(item, dict) else str(item)
                            if code in ['ค2010', 'งง30226']:
                                print(f"Found {code} in {sem} -> {k} -> {k2}")
    elif isinstance(content, list):
        for item in content:
            code = item.get('code') if isinstance(item, dict) else str(item)
            if code in ['ค2010', 'งง30226']:
                print(f"Found {code} in {sem}")
