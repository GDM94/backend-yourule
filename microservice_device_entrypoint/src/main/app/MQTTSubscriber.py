import paho.mqtt.client as mqtt


class Subscriber(object):
    def __init__(self, config, client_id, service, redis):
        self.r = redis
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
        keys = msg.topic.split("/")
        device_id = keys[-1]
        message_info = message_payload.split("/")
        measure = message_info[-1]
        expiration = message_info[0]
        print("[x] received message for device: {}; with measure: {} and expiration: {}".format(device_id, measure,
                                                                                                expiration))
        if self.r.exists("device:" + device_id + ":name") == 1:
            self.service.data_device_ingestion(device_id, measure, expiration)

    def callback_on_disconnect(self, paho_mqtt, userdata, rc):
        print("MQTT Subscriber successfull disconnected")
