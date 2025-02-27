#!/usr/bin/env python

import asyncio
import json
import clickhouse_connect
from datetime import datetime
import paho.mqtt.client as mqtt

mqttBroker = "127.0.0.1"
#mqttBroker = "broker.hivemq.com"
#mqttBroker = "mqtt.eclipseprojects.io"

dbclient = clickhouse_connect.get_client(
    host='localhost', port='7010', username='default')

dbclient.command(
    'CREATE TABLE IF NOT EXISTS table1 (ts DATETIME, user_name String, client_name String, param_name String, param_value Float64) ENGINE MergeTree ORDER BY client_name')


def on_connect(client, userdata, flags, rc):
    print("Connected with result code: "+str(rc))
    client.subscribe("topic1")


def on_message(client, userdata, msg):
    
    print('# in on_message function')

    data = []

    # print('# mqtt received: ', msg.payload)
    print('# mqtt received: ', msg.payload.decode())
    # print('# mqtt received - type: ', type(msg.payload.decode()))

    try:
        data = msg.payload.decode()
        data = json.loads(data)
        data[0] = datetime.fromtimestamp(data[0])

        print('# going to update db with: ', data)

        dbclient.insert('table1', [data], column_names=[
            'ts', 'user_name', 'client_name', 'param_name', 'param_value'])
        print()

    except Exception as e:
        print('# error in processing the recevied mqtt message: ', e)


client = mqtt.Client('xxx_receiver2')
client.connect(mqttBroker, 1883, 60)

client.on_connect = on_connect
client.on_message = on_message

print('# before loop_forever')
client.loop_forever()
print('# after loop_forever')
