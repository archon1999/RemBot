import os
import psutil


for proc in psutil.process_iter():
    if '0.0.0.0:8000' in proc.cmdline():
        proc.kill()


os.system('cd server && python3.10 manage.py runserver 0.0.0.0:8000 &')
