import paho.mqtt.client as mqtt
import time

# Define the MQTT broker address and port
broker_address = "127.0.0.1"
broker_port = 1883

# Define the client ID
client_id = "server-which-could-send-too"

# Callback function when a message is published
def on_publish(client, userdata, mid):
    print("Message Published")

# Create an MQTT client
client = mqtt.Client(client_id)

# Connect to the MQTT broker
client.connect(broker_address, broker_port)

def on_message(client, userdata, message):
    print(f"Received message from Server!! '{message.payload.decode()}' on topic '{message.topic}'")

client.on_message = on_message

client.subscribe('client-topic')

# Start the MQTT loop
client.loop_start()

while True:
    # Publish data to a topic
    message = "Hello from Server!!"
    client.publish("client-topic", message)
    
    # Wait for a while before publishing again
    time.sleep(1)

# Don't forget to handle cleanup when exiting your application
# client.loop_stop()
# client.disconnect()
