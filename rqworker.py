#!/usr/bin/env python
import os
import redis
from rq import Worker, Queue
from logger_custom import get_module_logger

logger = get_module_logger(__name__)

listen = ['app1']
redis_url = os.getenv('REDISTOGO_URL', 'redis://redis:6379')
conn = redis.from_url(redis_url)

if __name__ == '__main__':
    worker = Worker([Queue(name, connection=conn) for name in listen])
    worker.work()