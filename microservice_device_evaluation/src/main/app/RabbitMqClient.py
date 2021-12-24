import pika
import json
import time


class RabbitMQ(object):
    def __init__(self, app_id, service, config, mqtt):
        rabbitmq_server = config.get("RABBITMQ", "server")
        rabbitmq_port = int(config.get("RABBITMQ", "port"))
        virtual_host = config.get("RABBITMQ", "virtual_host")
        username = config.get("RABBITMQ", "username")
        password = config.get("RABBITMQ", "password")
        credentials = pika.PlainCredentials(username, password)
        self.mqtt_topic_switch = config.get("MQTT", "publish_topic_switch")
        self.mqtt_topic_servo = config.get("MQTT", "publish_topic_servo")
        self.mqtt_topic_expiration = config.get("MQTT", "publish_topic_expiration")
        self.params = pika.connection.ConnectionParameters(host=rabbitmq_server,
                                                           port=rabbitmq_port,
                                                           virtual_host=virtual_host,
                                                           credentials=credentials,
                                                           heartbeat=0)
        self.subscribe_queue = config.get("RABBITMQ", "subscribe_queue")
        self.publish_queue = config.get("RABBITMQ", "publish_queue")
        self.channel = None
        self.connection = None
        self.service = service
        self.mqtt = mqtt
        self.properties = pika.BasicProperties(
            app_id=app_id,
            content_type='application/json',
            content_encoding='utf-8',
            delivery_mode=2)

    def start_connection(self):
        if not self.connection or self.connection.is_closed:
            while not self.connection or self.connection.is_closed:
                try:
                    print("Connecting...")
                    self.connection = pika.BlockingConnection(self.params)
                except Exception as error:
                    print("Connection refused, try again in 10 s")
                    time.sleep(10)
            print("Connected!")
            self.channel = self.connection.channel()
            self.channel.basic_qos(prefetch_count=1)

    def close(self):
        if self.connection and self.connection.is_open:
            self.channel.stop_consuming()
            self.connection.close()

    def publish(self, msg, publish_queue):
        self.start_connection()
        # print("publish " + msg + " to queue " + publish_queue)
        self.channel.basic_publish(
            exchange='',
            routing_key=publish_queue,
            body=msg.encode(),
            properties=self.properties)

    def subscribe(self):
        print("Subscribe to " + self.subscribe_queue)
        self.channel.basic_consume(queue=self.subscribe_queue, on_message_callback=self.on_message_callback)
        self.channel.start_consuming()

    def on_message_callback(self, ch, method, properties, body):
        message = body.decode()
        payload = json.loads(message)
        print("[x] received message " + str(payload))
        device_id = str(payload["id"])
        measure = str(payload["measure"])
        expiration = str(payload["expiration"])
        self.service.check_device_registration(device_id)
        expiration_sync = self.service.expiration_evaluation(device_id, expiration)
        if expiration_sync != "false":
            topic = self.mqtt_topic_expiration + device_id
            self.mqtt.publish(topic, expiration_sync)
        trigger = self.service.measure_evaluation(device_id, measure)
        if trigger.type == "antecedent":
            if len(trigger.rules) > 0:
                output = json.dumps(trigger, default=lambda o: o.__dict__)
                self.publish(output, self.publish_queue)
        elif trigger.type == "switch":
            topic = self.mqtt_topic_switch + device_id
            self.mqtt.publish(topic, trigger.measure)
        elif trigger.type == "servo":
            topic = self.mqtt_topic_servo + device_id
            self.mqtt.publish(topic, trigger.measure)
        ch.basic_ack(delivery_tag=method.delivery_tag)
