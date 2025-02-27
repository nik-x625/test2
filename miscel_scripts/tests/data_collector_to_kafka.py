#!/usr/bin/env python

# This module collects the data from CPEs via MQTT and pushes to Kafka. 
# Another process, a consumer, will pick the data from Kafka and processes based on the policies.

import asyncio
import json
import clickhouse_connect
from datetime import datetime
import paho.mqtt.client as mqtt


from confluent_kafka import Producer
from faker import Faker
import json
import time
import logging
import random


# MQTT
mqttBroker = "127.0.0.1"
# mqttBroker = "broker.hivemq.com"
# mqttBroker = "mqtt.eclipseprojects.io"


# Kafka
kafka_producer = Producer({'bootstrap.servers': 'localhost:9092'})
print('Kafka Producer has been initiated...')


def receipt(err, msg):
    if err is not None:
        print('Error: {}'.format(err))
    else:
        message = 'Produced message on topic {} with value of {}\n'.format(
            msg.topic(), msg.value().decode('utf-8'))
        logger.info(message)
        print(message)


# ClickHouse
# dbclient = clickhouse_connect.get_client(
#     host='localhost', port='7010', username='default')

# dbclient.command(
#     'CREATE TABLE IF NOT EXISTS table1 (ts DATETIME, user_name String, client_name String, param_name String, param_value Float64) ENGINE MergeTree ORDER BY client_name')


def on_connect(client, userdata, flags, rc):
    print("Connected with result code: "+str(rc))
    client.subscribe("cpe_general_topic")


def on_message(client, userdata, msg):

    print()
    print('# in on_message function')

    data = []

    # print('# mqtt received: ', msg.payload)
    print('# mqtt received: ', msg.payload.decode())
    # print('# mqtt received - type: ', type(msg.payload.decode()))

    try:
        data = msg.payload.decode()
        data_json = data
        data = json.loads(data)
        data[0] = datetime.fromtimestamp(data[0])
        
        username = data[1]
        cpeid = data[2]
        user_cpe_kafka_topic = username+'___'+cpeid  # TODO: improve this later, the characters could be confused if used in cpeid or uername

        #print('# going to update db with: ', data)

        # dbclient.insert('table1', [data], column_names=[
            # 'ts', 'user_name', 'client_name', 'param_name', 'param_value'])
        # print()

        # for Kafka
        m = data_json
        print('# going to update db with data: ', data, '    to the Kafka topic: '+str(user_cpe_kafka_topic))
        kafka_producer.produce('aa.a___qq', m.encode('utf-8'), callback=receipt)

    except Exception as e:
        print('# error in processing the recevied mqtt message: ', e)


client = mqtt.Client('some_client_name_here1')
client.connect(mqttBroker, 1883, 60)

client.on_connect = on_connect
client.on_message = on_message

print('# before loop_forever')
client.loop_forever()
print('# after loop_forever')
