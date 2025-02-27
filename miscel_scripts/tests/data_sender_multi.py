#!/usr/bin/python
import paho.mqtt.client as mqtt
from random import randrange, uniform
import time
import numpy as np
import datetime
import json
import sys
from threading import Thread

mqttBroker = "127.0.0.1"


def create_random_data(user_name, client_name, param_name, u, sigma):
    ms = datetime.datetime.now()
    now = time.mktime(ms.timetuple())
    s = np.random.normal(u, sigma, 1)
    data = [now, user_name, client_name, param_name, s[0]]
    return data


def mqtt_establish(clientname):
    client = mqtt.Client(clientname)
    client.connect(mqttBroker)
    return client


def send_data(clientname, username):

    topic = 'topic1'
    client = None

    while True:

        # Establishing the mqtt connection if not exists
        if not client:
            try:
                client = mqtt_establish(clientname)
            except Exception as e:
                print('the initial connection attempt failed')
                time.sleep(1)
                print()
                continue

        try:
            if client._state != 0:
                print('# connection attempt failed, skipping data point...')
                continue
            else:
                data1 = create_random_data(
                    username, clientname, 'param1', 20, 5)
                data2 = create_random_data(
                    username, clientname, 'param2', 100, 5)
                res1 = client.publish(topic, json.dumps(data1))
                res2 = client.publish(topic, json.dumps(data2))
                print('The sending attempt has for data1 result: ',
                      (res1.is_published()), ' and data is: ', data1)
                print('The sending attempt has for data1 result: ',
                      (res2.is_published()), ' and data is: ', data2)

                sleeping_time = randrange(10, 100)/10
                print('# going to sleep for {} seconds'.format(sleeping_time))
                # print("Just published " + str(data) + " to broker")
                # print('client obj: '+str(dir(client)))

        except Exception as e:
            print('The error occured: {}, skipping this data point...'.format(e))
            client = None

        print()
        time.sleep(sleeping_time)


if __name__ == "__main__":
    cpe_count = 30
    client_prefix = 'cpe'
    client_list = [client_prefix+str(x) for x in range(1, cpe_count)]

    username = 'a@b.c'

    for clientname in client_list:  # [start:start+step]:
        try:
            t = Thread(target=send_data, args=(clientname, username))
            t.start()
        except KeyboardInterrupt:
            print("Ctrl-c pressed ...")
            sys.exit(1)
