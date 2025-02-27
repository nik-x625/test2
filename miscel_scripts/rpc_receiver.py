#!/usr/bin/env python
import asyncio
import websockets
import json
import clickhouse_connect
from datetime import datetime
import paho.mqtt.client as mqtt

mqttBroker = "127.0.0.1"
#mqttBroker = "broker.hivemq.com"
#mqttBroker = "mqtt.eclipseprojects.io"


def on_connect(client, userdata, flags, rc):
    print("Connected with result code: "+str(rc))
    client.subscribe("topic-rpc-client1")

def on_message(client, userdata, msg):
    data = []
    
    try:
        
        data = msg.payload.decode()
        data = json.loads(data)
        
        print('# command received from server to client is: '+str(data))
        print()

    except Exception as e:
        print('# error in processing the recevied mqtt message: ', e)


client = mqtt.Client('rpc command receiver - living in client')
client.connect(mqttBroker, 1883, 60)

client.on_connect = on_connect
client.on_message = on_message

client.loop_forever()
