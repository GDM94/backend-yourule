import paho.mqtt.client as PahoMQTT
from os.path import dirname, join, abspath
import configparser
from .ConsequentServiceEvaluationImpl import ConsequentServiceEvaluation


class Subscriber(object):
    def __init__(self, client_id, service):
        config = self.read_config()
        self.client = PahoMQTT.Client(client_id, True)
        self.BROKER = config.get("MQTT", "broker")
        self.PORT = int(config.get("MQTT", "port"))
        self.SUBSCRIBE_TOPIC = config.get("MQTT", "subscribe_topic")
        self.PUBLISH_TOPIC = config.get("MQTT", "publish_topic")
        self.IS_SUBSCRIBER = True
        # register the callback
        self.client.on_connect = self.callback_on_connect
        self.client.on_message = self.callback_on_message_received
        self.client.on_disconnect = self.callback_on_disconnect
        self.service = service

    def read_config(self):
        d = dirname(dirname(dirname(abspath(__file__))))
        config_path = join(d, 'properties', 'app-config.ini')
        config = configparser.ConfigParser()
        config.read(config_path)
        return config

    def start_connection(self):
        # manage connection to broker
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

    def publish(self, device_id, msg):
        # print("publish")
        topic = self.PUBLISH_TOPIC+device_id
        self.client.publish(topic, msg, 2)

    def callback_on_connect(self, paho_mqtt, userdata, flags, rc):
        print("Connected to %s with result code: %d" % (self.BROKER, rc))

    def callback_on_message_received(self, paho_mqtt, userdata, msg):
        message_payload = msg.payload.decode("utf-8")
        print("MQTT MESSAGE topic: {}; payload:{}".format(msg.topic, message_payload))
        output = self.service.consequent_evaluation(message_payload)
        n = len(output["device_id"])
        if n > 0:
            for idx in range(n):
                device_id = output["device_id"][idx]
                measure = output["measure"][idx]
                self.publish(self.PUBLISH_TOPIC+device_id, measure)

    def callback_on_disconnect(self, paho_mqtt, userdata, rc):
        print("MQTT Subscriber successfull disconnected")
