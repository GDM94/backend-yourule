import paho.mqtt.client as mqtt
import os
import sys


class Subscriber(object):
    def __init__(self, config, client_id, service):
        self.client = mqtt.Client(client_id, True)
        self.BROKER = config.get("MQTT", "broker")
        self.PORT = int(config.get("MQTT", "port"))
        self.SUBSCRIBE_TOPIC = config.get("MQTT", "subscribe_topic")
        self.IS_SUBSCRIBER = True
        self.service = service
        # register the callback
        self.client.on_connect = self.callback_on_connect
        self.client.on_message = self.callback_on_message_received

    def start_connection(self):
        try:
            self.client.username_pw_set("subscriber", "mqtt")
            self.client.connect(self.BROKER, self.PORT)
            self.client.loop_forever()
        except Exception as error:
            print(repr(error))
            self.restart()

    def subscribe(self):
        print("subscribing to topic: " + self.SUBSCRIBE_TOPIC)
        self.client.subscribe(self.SUBSCRIBE_TOPIC, 2)

    def publish(self, topic, payload):
        print("publish")
        self.client.publish(topic, payload, 2)

    def callback_on_connect(self, paho_mqtt, userdata, flags, rc):
        print("Connected to %s with result code: %d" % (self.BROKER, rc))
        self.subscribe()

    def callback_on_message_received(self, paho_mqtt, userdata, msg):
        message_payload = msg.payload.decode("utf-8")
        keys = msg.topic.split("/")
        device_id = keys[-1]
        message_info = message_payload.split("/")
        measure = message_info[-1]
        expiration = message_info[0]
        # print("[x] received message for device: {}; with measure: {} and expiration: {}".format(device_id, measure,
        # expiration))
        self.service.data_device_ingestion(device_id, measure, expiration)

    def restart(self):
        print("restart")
        os.execv(sys.executable, ['python -u'] + sys.argv)
