# redis_utils.py

import redis
from rq import Queue#, Connection

redis_conn = redis.Redis(host='redis', port=6379, db=0)
redis_queue = Queue('app1', connection=redis_conn)

def enqueue_long_running_function(func, *args):
    #with Connection(redis_conn):
        redis_queue.enqueue(func, *args)
