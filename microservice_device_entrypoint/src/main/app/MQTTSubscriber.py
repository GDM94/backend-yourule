import paho.mqtt.client as mqtt
import requests


class Subscriber(object):
    def __init__(self, config, client_id):
        self.client = mqtt.Client(client_id, True)
        self.BROKER = config.get("MQTT", "broker")
        self.PORT = int(config.get("MQTT", "port"))
        self.SUBSCRIBE_TOPIC = config.get("MQTT", "subscribe_topic")
        self.backend_server = config.get("BACKEND", "ip")
        self.IS_SUBSCRIBER = True
        # register the callback
        self.client.on_connect = self.callback_on_connect
        self.client.on_message = self.callback_on_message_received

    def start_connection(self):
        self.client.username_pw_set("subscriber", "mqtt")
        self.client.connect(self.BROKER, self.PORT)
        self.client.loop_forever()

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
        print("[x] received message for device={} measure={} expiration={}".format(device_id, measure, expiration))
        payload = {"device_id": device_id, "measure": measure, "expiration": expiration}
        requests.post(self.backend_server, json=payload, headers={"Content-Type": "application/json"})
