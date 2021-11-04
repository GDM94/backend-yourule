import pika
import time
import json


class RabbitMQ(object):
    def __init__(self, app_id, service, mqtt, config):
        rabbitmq_server = config.get("RABBITMQ", "server")
        rabbitmq_port = int(config.get("RABBITMQ", "port"))
        virtual_host = config.get("RABBITMQ", "virtual_host")
        username = config.get("RABBITMQ", "username")
        password = config.get("RABBITMQ", "password")
        credentials = pika.PlainCredentials(username, password)
        self.params = pika.connection.ConnectionParameters(host=rabbitmq_server,
                                                           port=rabbitmq_port,
                                                           virtual_host=virtual_host,
                                                           credentials=credentials,
                                                           heartbeat=0)
        self.subscribe_queue = config.get("RABBITMQ", "subscribe_queue")
        self.publish_queue = config.get("RABBITMQ", "publish_queue")
        self.mqtt_publish_topic = config.get("MQTT", "publish_topic")
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

    def publish(self, msg):
        # print("publish " + msg)
        self.start_connection()
        self.channel.basic_publish(
            exchange='',
            routing_key=self.publish_queue,
            body=msg.encode(),
            properties=self.properties)

    def subscribe(self):
        print("Subscribe to " + self.subscribe_queue)
        self.channel.basic_consume(queue=self.subscribe_queue, on_message_callback=self.on_message_callback)
        self.channel.start_consuming()

    def on_message_callback(self, ch, method, properties, body):
        message = body.decode()
        print("[x] received message " + message)
        message_dict = json.loads(message)
        user_id = str(message_dict["user_id"])
        rule_id = str(message_dict["rule_id"])
        output = self.service.consequent_evaluation(user_id, rule_id)
        for trigger in output:
            topic = self.mqtt_publish_topic + trigger["device_id"]
            payload = trigger["measure"]+"/"+trigger["delay"]
            self.mqtt.publish(topic, payload)
        ch.basic_ack(delivery_tag=method.delivery_tag)
