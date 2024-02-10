import os
import time
from threading import Thread
from functools import partial

for game in range(2):
    Thread(target=partial(os.system,'python main.py')).start()
    time.sleep(1)
