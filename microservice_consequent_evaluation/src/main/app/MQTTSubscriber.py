import paho.mqtt.client as PahoMQTT


class Subscriber(object):
    def __init__(self, client_id, config):
        self.client = PahoMQTT.Client(client_id, True)
        self.BROKER = config.get("MQTT", "broker")
        self.PORT = int(config.get("MQTT", "port"))
        self.SUBSCRIBE_TOPIC = config.get("MQTT", "subscribe_topic")
        self.PUBLISH_TOPIC = config.get("MQTT", "publish_topic")
        self.IS_SUBSCRIBER = True
        # register the callback
        self.client.on_connect = self.callback_on_connect
        self.client.on_disconnect = self.callback_on_disconnect


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
        print("publish message: {} to topic: {}".format(msg, topic))
        self.client.publish(topic, msg, 2)

    def callback_on_connect(self, paho_mqtt, userdata, flags, rc):
        print("Connected to %s with result code: %d" % (self.BROKER, rc))

    def callback_on_disconnect(self, paho_mqtt, userdata, rc):
        print("MQTT Subscriber successfull disconnected")
