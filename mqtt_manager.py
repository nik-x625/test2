#!/usr/bin/env python
from datetime import datetime
import paho.mqtt.client as mqtt
import json
import clickhouse_connect
from datetime import datetime
import paho.mqtt.client as mqtt
import threading
from logger_custom import get_module_logger
from mongodb_module import update_device_info, update_device_params
logger = get_module_logger(__name__)


# dbclient = clickhouse_connect.get_client(
#     host='localhost', port='7010', username='default')

# dbclient.command(
#     'CREATE TABLE IF NOT EXISTS table1 (ts DATETIME, user_name String, client_name String, param_name String, param_value Float64) ENGINE MergeTree ORDER BY client_name')


MQTT_BROKER_HOST = 'mosquitto'  # Replace with your broker's hostname or IP
MQTT_BROKER_PORT = 1883  # Replace with your broker's port
#MQTT_TOPIC = 'ser_to_cl_topic1'  # Replace with the desired MQTT topic

client = mqtt.Client()

# def on_connect(client, userdata, flags, rc):
#     print(f'Connected to MQTT Broker with result code {rc}')
#     client.subscribe(MQTT_TOPIC)


def on_message(client, userdata, msg):

    data = []
    keyvalue = {}

    # print('# mqtt received: ', msg.payload)
    #logger.debug('# mqtt received: '+str(msg.payload.decode()))
    # print('# mqtt received - type: ', type(msg.payload.decode()))

    try:
        data = msg.payload.decode()
        message = json.loads(data)
        logger.debug('# json of the data arrived in mqtt is: '+str(message))
        
        
        
        client_name = message.get('client_name', '')
        user_name = message.get('user_name', '')
        
        keyvalue = {'ts_last_message': datetime.now() }
        
        if message['message_type'] == 'cli_response':
            
            
            last_cli_response = message['param_subtree']['cli_response_body']
            
            # to store in mongodb
            keyvalue['last_cli_response']  = last_cli_response
            
            logger.debug('# cli response arrived, response message is: '+str(message))
            
            
                    
        elif message['message_type'] == 'periodic':

            timestamp = datetime.utcfromtimestamp(message.get('ts'))
            param_subtree = message.get('param_subtree', {})
            
            mongo_update_res = update_device_params(user_name, client_name, timestamp, param_subtree)
            
            logger.debug('# mongo_update_res: '+str(mongo_update_res))

            #for param_name, param_value in param_subtree.items():
            #    time_series_doc = [timestamp, user_name, client_name, param_name, param_value]
                
            #    logger.debug('# time series data to store in mongodb: '+str(time_series_doc))
                                
                #dbclient.insert('table1', [clickhouse_data], column_names=[
                #'ts', 'user_name', 'client_name', 'param_name', 'param_value'])
                
                
                
                
        
        update_result = update_device_info(client_name, user_name, keyvalue)
        if update_result:
            logger.debug('# the mongo update for cli_response was successful!')
        else:
            logger.debug('# the mongo update for cli_response failed!')            

    except Exception as e:
        logger.debug('# error in processing the recevied mqtt message: '+str(e))


#client = mqtt.Client('qlines_mqtt_manager')
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)


client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)

# client.on_connect = on_connect
client.on_message = on_message
client.subscribe("us_topic_for_all")

# client.loop_start()


def mqtt_loop():
    client.loop_forever()


mqtt_thread = threading.Thread(target=mqtt_loop)
mqtt_thread.start()


def connect_to_mqtt_broker():
    logger.debug('# in the function connect_to_mqtt_broker')
    # client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)
    # logger.debug('# connected')
    # client.loop_start()  # Start the MQTT client loop
    return client
