import os

if not os.getuid == 0:
    print('Please run as root')
    exit(1)
os.system('pip3 install bs4')
os.system('pip3 install requests')
