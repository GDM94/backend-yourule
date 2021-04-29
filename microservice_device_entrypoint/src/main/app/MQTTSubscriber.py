import paho.mqtt.client as mqtt
from os.path import dirname, join, abspath
import configparser
import json


class Subscriber(object):
    def __init__(self, client_id, service):
        config = self.read_config()
        self.client = mqtt.Client(client_id, True)
        self.BROKER = config.get("MQTT", "broker")
        self.PORT = int(config.get("MQTT", "port"))
        self.SUBSCRIBE_TOPIC = config.get("MQTT", "subscribe_topic")
        self.IS_SUBSCRIBER = True
        self.service = service
        # register the callback
        self.client.on_connect = self.callback_on_connect
        self.client.on_message = self.callback_on_message_received
        self.client.on_disconnect = self.callback_on_disconnect

    def read_config(self):
        d = dirname(dirname(dirname(abspath(__file__))))
        config_path = join(d, 'properties', 'app-config.ini')
        config = configparser.ConfigParser()
        config.read(config_path)
        return config

    def start_connection(self):
        # manage connection to broker
        self.client.username_pw_set("subscriber", "mqtt")
        self.client.connect(self.BROKER, self.PORT)
        self.client.loop_start()

    def stop_connection(self):
        print("MQTT shutdown")
        if self.IS_SUBSCRIBER:
            # remember to unsuscribe if it is working also as subscriber
            self.client.unsubscribe(self.SUBSCRIBE_TOPIC)
        self.client.loop_stop()
        self.client.disconnect()

    def subscribe(self):
        self.client.subscribe(self.SUBSCRIBE_TOPIC, 2)

    def publish(self, topic, payload):
        print("publish")
        self.client.publish(topic, payload, 2)

    def callback_on_connect(self, paho_mqtt, userdata, flags, rc):
        print("Connected to %s with result code: %d" % (self.BROKER, rc))

    def callback_on_message_received(self, paho_mqtt, userdata, msg):
        message_payload = msg.payload.decode("utf-8")
        print("[x] received topic: {}; payload: {}".format(msg.topic, message_payload))
        self.service.data_device_ingestion(msg.topic, message_payload)

    def callback_on_disconnect(self, paho_mqtt, userdata, rc):
        print("MQTT Subscriber successfull disconnected")
