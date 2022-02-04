import pika
import time
import json
import requests
from ruleapp.Devices.DeviceId import SWITCH, SERVO


class RabbitMQ(object):
    def __init__(self, app_id, config):
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
        self.mqtt_switch = config.get("MQTT", "mqtt_switch")
        self.mqtt_servo = config.get("MQTT", "mqtt_servo")
        self.mqtt_publisher_ip = config.get("MQTT", "ip")
        self.backend_server = config.get("BACKEND", "ip")
        self.channel = None
        self.connection = None
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
        payload = json.loads(message)
        response = requests.post(self.backend_server, json=payload, headers={"Content-Type": "application/json"})
        output = response.json()
        trigger_list = output["output"]
        for trigger in trigger_list:
            topic = ""
            if "SWITCH" in trigger["device_id"]:
                topic = self.mqtt_switch + trigger["device_id"]
            elif "SERVO" in trigger["device_id"]:
                topic = self.mqtt_servo + trigger["device_id"]
            url = self.mqtt_publisher_ip + topic
            payload = {"message": trigger["measure"] + "/" + trigger["delay"]}
            requests.post(url, json.dumps(payload))
        ch.basic_ack(delivery_tag=method.delivery_tag)
