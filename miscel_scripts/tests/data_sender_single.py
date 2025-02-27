#!/usr/bin/python
'''
module doc bla bla
'''
import time
import datetime
import json
import sys
import getopt
import paho.mqtt.client as mqtt
import numpy as np


mqttBroker = "127.0.0.1"
#mqttBroker = "broker.hivemq.com"
#mqttBroker = "mqtt.eclipseprojects.io"


def getargs(argv):
    arg_username = ""
    arg_clientname = ""
    arg_help = "{0} -u <username> -c <clientname> -t <topic>".format(argv[0])

    try:
        opts, args = getopt.getopt(argv[1:], "hu:c:t:", [
                                   "help", "username=", "clientname=", "topic="])
    except:
        print(arg_help)
        sys.exit(2)

    if not opts:
        print(arg_help)
        sys.exit(2)

    for opt, arg in opts:

        if opt in ("-h", "--help"):
            print(arg_help)  # print the help message
            sys.exit(2)
        elif opt in ("-u", "--username"):
            arg_username = arg
        elif opt in ("-c", "--clientname"):
            arg_clientname = arg
        elif opt in ("-t", "--topic"):
            arg_topic = arg
    return {'username': arg_username, 'clientname': arg_clientname, 'topic': arg_topic}


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


client = None

if __name__ == "__main__":

    commands = getargs(sys.argv)
    username = commands['username']
    clientname = commands['clientname']
    topic = commands['topic']

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
                #print("Just published " + str(data) + " to broker")
                #print('client obj: '+str(dir(client)))

        except Exception as e:
            print('The error occured: {}, skipping this data point...'.format(e))
            client = None

        print()
        time.sleep(1)

