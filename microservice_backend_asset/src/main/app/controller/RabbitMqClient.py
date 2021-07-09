import pika
import time


class RabbitMQ(object):
    def __init__(self, app_id, config):
        rabbitmq_server = config.get("RABBITMQ", "server")
        rabbitmq_port = int(config.get("RABBITMQ", "port"))
        virtual_host = config.get("RABBITMQ", "virtual_host")
        username = config.get("RABBITMQ", "username")
        password = config.get("RABBITMQ", "password")
        credentials = pika.PlainCredentials(username, password)
        print(rabbitmq_server)
        self.params = pika.connection.ConnectionParameters(host=rabbitmq_server,
                                                           port=rabbitmq_port,
                                                           virtual_host=virtual_host,
                                                           credentials=credentials,
                                                           heartbeat=0)
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

    def close(self):
        if self.connection and self.connection.is_open:
            self.channel.stop_consuming()
            self.connection.close()

    def publish(self, publish_queue, msg):
        print("publish " + msg)
        self.start_connection()
        self.channel.basic_publish(
            exchange='',
            routing_key=publish_queue,
            body=msg.encode(),
            properties=self.properties)


