import os
import psutil


for proc in psutil.process_iter():
    if 'RemBot1' in proc.cwd() and 'python3.10' in proc.cmdline():
        if 'restart_bot.py' not in proc.cmdline():
            proc.kill()


os.system('cd server && nohup python3.10 manage.py runserver 0.0.0.0:8001 &')
os.system('cd server && nohup python3.10 manage.py qcluster &')
os.system('cd client && nohup python3.10 bot.py rem_bot1 &')
