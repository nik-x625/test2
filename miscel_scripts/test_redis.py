'''
import redis
from rq import Queue
from email_module import send_general_text_email

# for long running functions
r = redis.Redis()
q = Queue('app1', connection=r)

q.enqueue(send_general_text_email,'some_text','some_subject')

'''


from redis_utils import enqueue_long_running_function
from email_module import *


enqueue_long_running_function(send_general_text_email, 'test_body', 'test_sub')
