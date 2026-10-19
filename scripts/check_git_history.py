import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')

res = subprocess.run(['git', 'log', '-n', '10', '--name-status'], capture_output=True, text=True, encoding='utf-8')
lines = res.stdout.split('\n')
for line in lines:
    if '09_หลักสูตรสถานศึกษา' in line or 'school_courses' in line or 'catalog' in line:
        print(line)
