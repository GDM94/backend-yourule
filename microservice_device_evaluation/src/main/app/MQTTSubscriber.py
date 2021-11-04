import paho.mqtt.client as PahoMQTT
from os.path import dirname, join, abspath
import configparser


class Subscriber(object):
    def __init__(self, client_id):
        config = self.read_config()
        self.client = PahoMQTT.Client(client_id, True)
        self.BROKER = config.get("MQTT", "broker")
        self.PORT = int(config.get("MQTT", "port"))
        self.PUBLISH_TOPIC_SWITCH = config.get("MQTT", "publish_topic_switch")
        self.PUBLISH_TOPIC_EXPIRATION = config.get("MQTT", "publish_topic_expiration")
        self.SUBSCRIBE_TOPIC = ""
        self.IS_SUBSCRIBER = False
        # register the callback
        self.client.on_connect = self.callback_on_connect
        self.client.on_disconnect = self.callback_on_disconnect

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

    def publish(self, topic, msg):
        print("publish to topic: {}, message: {}".format(topic, msg))
        self.client.publish(topic, msg, 2)

    def callback_on_connect(self, paho_mqtt, userdata, flags, rc):
        print("Connected to %s with result code: %d" % (self.BROKER, rc))

    def callback_on_disconnect(self, paho_mqtt, userdata, rc):
        print("MQTT Subscriber successfull disconnected")
