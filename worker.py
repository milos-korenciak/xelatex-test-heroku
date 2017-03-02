import os
from redis import Redis
import time
import datetime
import random
from rq import Worker, Queue, Connection

listen = ['default']

redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
redis = Redis()
conn = redis.from_url(redis_url)
start_time = datetime.datetime.now()

if __name__ == '__main__':
    i = random.random()
    while 1:
        print("Hello worker {} running {} at {}!".format(i,
              datetime.datetime.now() - start_time, datetime.datetime.now()))
        time.sleep(60)

    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()

