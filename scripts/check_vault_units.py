import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

codes = ['ง30222', 'ง30223', 'ว30221', 'ว30267', 'ว30268', 'ศ32201']
vault_root = os.path.join("Curriculum_Vault", "09_หลักสูตรสถานศึกษา")

for code in codes:
    for root, dirs, files in os.walk(vault_root):
        for f in files:
            if f.startswith(code):
                p = os.path.join(root, f)
                with open(p, 'r', encoding='utf-8') as fp:
                    txt = fp.read()
                print(f"=== {code} ({f}) ===")
                # find table
                lines = txt.split('\n')
                in_table = False
                for line in lines:
                    if '| หน่วยที่ |' in line or '| :---: |' in line:
                        in_table = True
                        print(line)
                    elif in_table:
                        if line.startswith('|'):
                            print(line)
                        else:
                            in_table = False
                print()
