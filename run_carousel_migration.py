import subprocess
import sys
import os

# Change to the correct directory
os.chdir(r'c:\Users\Little Human\Desktop\RootsParty')

# Run makemigrations
result = subprocess.run([sys.executable, 'manage.py', 'makemigrations', 'core'], capture_output=True, text=True)
print(result.stdout)
print(result.stderr)

# Run migrate
if result.returncode == 0:
    result2 = subprocess.run([sys.executable, 'manage.py', 'migrate'], capture_output=True, text=True)
    print(result2.stdout)
    print(result2.stderr)
