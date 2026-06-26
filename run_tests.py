import subprocess
result = subprocess.run(['python', '-c', '''
import sys
sys.stdout.reconfigure(encoding="utf-8")
exec(open("test_api.py", encoding="utf-8").read())
'''], capture_output=True, text=True, encoding='utf-8')
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print("Return code:", result.returncode)
