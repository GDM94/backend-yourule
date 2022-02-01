import paho.mqtt.client as mqtt


class Publisher(object):
    def __init__(self, client_id, broker, port):
        self.client = mqtt.Client(client_id, True)
        self.BROKER = broker
        self.PORT = int(port)
        self.IS_SUBSCRIBER = False
        self.SUBSCRIBE_TOPIC = ""
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
            self.client.unsubscribe(self.SUBSCRIBE_TOPIC)
        self.client.loop_stop()
        self.client.disconnect()

    def subscribe(self):
        self.client.subscribe(self.SUBSCRIBE_TOPIC, 2)

    def publish(self, topic, msg):
        print("publish topic: {} payload:{}".format(topic, msg))
        self.client.publish(topic, msg, 2)

    def callback_on_connect(self, paho_mqtt, userdata, flags, rc):
        print("Connected to %s with result code: %d" % (self.BROKER, rc))

    def callback_on_disconnect(self, paho_mqtt, userdata, rc):
        print("MQTT Client successfull disconnected")
        self.stop_connection()
        self.start_connection()
        self.subscribe()
