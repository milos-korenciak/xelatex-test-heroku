import time
import datetime
import random
i = random.random()
while 1:
    print("Hello worker %s on %s!"%(i, datetime.datetime.now()))
    time.sleep(30)
