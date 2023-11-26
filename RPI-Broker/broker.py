# Raspberry Pi script (broker.py)
import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt

GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)

def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    if payload == 'activate':
        GPIO.output(18, GPIO.HIGH)
    elif payload == 'deactivate':
        GPIO.output(18, GPIO.LOW)

broker_address = "192.168.71.214"  # Use the IP address or hostname of your Raspberry Pi
client = mqtt.Client()
client.on_message = on_message
client.connect(broker_address, 1883, 60)
client.subscribe("actuator/control")
client.loop_forever()
