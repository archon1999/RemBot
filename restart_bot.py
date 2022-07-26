import os
import psutil


for proc in psutil.process_iter():
    if 'rem_bot' in proc.cmdline():
        proc.kill()


os.system('cd client && python3.10 bot.py rem_bot &')
