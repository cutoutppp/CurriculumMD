import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')

res = subprocess.run(['git', 'log', '-n', '25', '--oneline'], capture_output=True, text=True, encoding='utf-8')
print(res.stdout)
