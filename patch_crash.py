import sys
import traceback
import os

path = r'D:\Development\SkySpotter\src\main.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

if 'global_exception_handler' not in content:
    hook_code = '''
import sys
import traceback
import os

def global_exception_handler(exc_type, exc_value, exc_traceback):
    try:
        log_dir = os.path.join(os.environ.get('LOCALAPPDATA', 'C:'), "SkySpotter", "logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "crash.log")
        with open(log_file, "a", encoding="utf-8") as f:
            import datetime
            f.write(f"\\n[{datetime.datetime.now()}] Uncaught exception:\\n")
            traceback.print_exception(exc_type, exc_value, exc_traceback, file=f)
            f.write("-" * 80 + "\\n")
    except Exception:
        pass
    sys.__excepthook__(exc_type, exc_value, exc_traceback)

sys.excepthook = global_exception_handler
'''
    if 'import sys' in content:
        content = content.replace('import sys', hook_code, 1)
    else:
        content = hook_code + '\n' + content

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print('Added crash handler to SkySpotter/src/main.py')
else:
    print('Crash handler already exists in SkySpotter/src/main.py')
