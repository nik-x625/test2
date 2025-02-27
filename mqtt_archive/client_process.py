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
# mqttBroker = "broker.hivemq.com"
# mqttBroker = "mqtt.eclipseprojects.io"
response_to_us = None

def getargs(argv):
    arg_username = ""
    arg_clientname = ""
    arg_help = "{0} -u <username> -c <clientname>".format(argv[0])

    try:
        opts, args = getopt.getopt(argv[1:], "hu:c:t:", [
                                   "help", "username=", "clientname="])
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
        # elif opt in ("-t", "--topic"):
        #    arg_topic = arg
    # , 'topic': arg_topic}
    return {'username': arg_username, 'clientname': arg_clientname}


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


def on_message(client, userdata, message_initial):
    #message = json.loads(str(message_initial.payload.decode()))
    print('# message received: '+str(message_initial.payload.decode()))
    message = message_initial.payload.decode()
    message = message.replace("'", "\"")
    message = json.loads(message)
    global response_to_us
    print('# the response_to_us initial is: '+str(response_to_us))
    message['read'] = 1 
    response_to_us = message
    print('# message: '+str(message))
    #print('# message type: '+str(type(message_initial.payload.decode())))
    #print(
    #    f"Received message in the client:   '{message}' on topic '{message_initial.topic}'")


client = None

if __name__ == "__main__":

    commands = getargs(sys.argv)
    username = commands['username']
    clientname = commands['clientname']
    # topic = commands['topic']

    # to send data from client to server
    # username = 'a@a.a'
    # clientname = 'mx' #'g_4334_6gre' #'mx'
    topic_us = 'us_topic_for_all'  # username + '_' + clientname + '_' + 'us'

    # to receive data from the server
    topic_ds = username + '_' + clientname + '_' + 'ds'

    while True:

        # Establishing the mqtt connection if not exists
        if (not client):  # or (client._state != 0):
            try:

                print('# no client is defined, going to create the handler.')
                client = mqtt_establish(clientname)
                time.sleep(0.5)

                # subscribe to the topic, to receive messages from server
                client.on_message = on_message
                client.subscribe(topic_ds)

                print('just after subscribe')

                # to receive messages from server
                time.sleep(0.5)
                client.loop_start()
                time.sleep(0.5)

            except Exception as e:
                print('the initial connection attempt failed, error: '+str(e))
                time.sleep(1)
                print()
                continue

        try:
            if 0:  # client._state != 0:
                print(
                    '# connection attempt failed, skipping data point..client._state is: '+str(client._state))
                time.sleep(1)
                continue
            else:

                # print('# good!, state is 0 and going to publish some messages')
                data1 = create_random_data(
                    username, clientname, 'param1', 20, 5)
                data2 = create_random_data(
                    username, clientname, 'param2', 100, 5)
                res1 = client.publish(topic_us, json.dumps(data1))
                res2 = client.publish(topic_us, json.dumps(data2))
                

                    
                time.sleep(0.2)
                print('The sending attempt has for data1 result: ',
                      (res1.is_published()), ' and data is: ', data1)
                print('The sending attempt has for data1 result: ',
                      (res2.is_published()), ' and data is: ', data2)
                

        except Exception as e:
            print('The error occured: {}, skipping this data point...'.format(e))
            client = None

        print()
        time.sleep(5)
