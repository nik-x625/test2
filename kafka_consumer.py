"""original script here: https://github.com/anbento0490/tutorials/tree/master/kafka_demo"""

from confluent_kafka import Consumer
import time
################
c = Consumer({'bootstrap.servers': 'localhost:9092',
             'group.id': 'python-consumer',
              'auto.offset.reset': 'earliest'})

print('Kafka Consumer has been initiated...')

print('Available topics to consume: ', c.list_topics().topics)
c.subscribe(['topic_x7'])
################


def main():
    while True:
        msg = c.poll(1)  # timeout
        print('# msg is: '+str(msg))
        if msg is None:
            continue

        if msg.error():
            print('Error: {}'.format(msg.error()))
            continue
        data = msg.value().decode('utf-8')
        print(data)
        # time.sleep(0.1)
    c.close()


if __name__ == '__main__':
    main()
