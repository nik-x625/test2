import paho.mqtt.client as mqtt
import time

# Define the MQTT broker address and port
broker_address = "127.0.0.1"
broker_port = 1883

# Define the client ID
client_id = "server-simple"

# Callback function when a message is received
def on_message(client, userdata, message):
    print(f"Received message from Client!! '{message.payload.decode()}' on topic '{message.topic}'")

# Create an MQTT client
client = mqtt.Client(client_id)

# Set the callback function for message reception
client.on_message = on_message

# Connect to the MQTT broker
client.connect(broker_address, broker_port)

# Subscribe to a topic where the client expects messages from the server
client.subscribe("client-topic")

# Start the MQTT loop to handle incoming messages
client.loop_forever()
