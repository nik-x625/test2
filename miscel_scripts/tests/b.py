import paho.mqtt.client as mqtt

# MQTT broker configuration
broker_address = "localhost"
broker_port = 1883

# Define a callback function to handle incoming messages
def on_message(client, userdata, message):
    # Print out the received message
    print("Received message:", str(message.payload.decode("utf-8")))

# Create a MQTT client instance
client = mqtt.Client()

# Connect to the MQTT broker
client.connect(broker_address, broker_port)

# Set the message callback function
client.on_message = on_message

# Start the MQTT loop to receive incoming messages
client.loop_start()

# Publish a message to the server
client.publish("test/topic", "Hello, MQTT")

# Wait for incoming messages to be processed
while True:
    pass

# Disconnect from the MQTT broker
client.loop_stop()
client.disconnect()

