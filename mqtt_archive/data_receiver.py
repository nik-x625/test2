#!/usr/bin/env python

import json
import time
import clickhouse_connect
from datetime import datetime
import paho.mqtt.client as mqtt
import threading

mqttBroker = "127.0.0.1"
#mqttBroker = "broker.hivemq.com"
#mqttBroker = "mqtt.eclipseprojects.io"

dbclient = clickhouse_connect.get_client(
    host='localhost', port='7010', username='default')

dbclient.command(
    'CREATE TABLE IF NOT EXISTS table1 (ts DATETIME, user_name String, client_name String, param_name String, param_value Float64) ENGINE MergeTree ORDER BY client_name')


# def on_connect(client, userdata, flags, rc):
#     print("Connected with result code: "+str(rc))
#     client.subscribe("cl_to_ser_topic1")


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


client = mqtt.Client('receiver_clickhouse')
client.connect(mqttBroker, 1883, 60)

#client.on_connect = on_connect
client.on_message = on_message
client.subscribe("us_topic_for_all")



#client.loop_start()
def mqtt_loop():
    client.loop_forever()

mqtt_thread = threading.Thread(target=mqtt_loop)
mqtt_thread.start()



# while True:
#     # Publish data to a topic
#     message = "Hello from Server!!"
#     client.publish("ser_to_cl_topic1", message)
    
#     # Wait for a while before publishing again
#     time.sleep(3)
