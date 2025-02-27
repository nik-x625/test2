"""original script here: https://github.com/anbento0490/tutorials/tree/master/kafka_demo"""

from confluent_kafka import Producer
from faker import Faker
import json
import time
import logging
import random

fake=Faker()

logging.basicConfig(format='%(asctime)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename='producer.log',
                    filemode='w')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

####################
p=Producer({'bootstrap.servers':'localhost:9092'})
print('Kafka Producer has been initiated...')
#####################
def receipt(err,msg):
    if err is not None:
        print('Error: {}'.format(err))
    else:
        message = 'Produced message on topic {} with value of {}\n'.format(msg.topic(), msg.value().decode('utf-8'))
        logger.info(message)
        print(message)
        
#####################
def main():
    count = 0
    while True: #for i in range(10):
        print('')
        print('going to create the data.........................')
        data={
           'user_id': fake.random_int(min=20000, max=100000),
           'user_name':fake.name(),
           #'user_address':fake.street_address() + ' | ' + fake.city() + ' | ' + fake.country_code(),
           #'platform': random.choice(['Mobile', 'Laptop', 'Tablet']),
           #'signup_at': str(fake.date_time_this_month()),
           'count' : str(count)
           }
        count = count +1
        m=json.dumps(data)
        print('going to poll')
        #p.poll(1)
        
        print('poll done')
        
        p.produce('topic_x7', m.encode('utf-8'),callback=receipt)
        
        print('produce done for count: '+str(count))
        
        p.flush()
        
        print('flush done')
        time.sleep(0.5)
        
if __name__ == '__main__':
    main()