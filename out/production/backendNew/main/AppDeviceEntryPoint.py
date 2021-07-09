from app.RabbitMqClient import RabbitMQ
from app.MQTTSubscriber import Subscriber
import time
import random
import string

client_id = random_client_id = 'device_entrypoint'.join(random.choices(string.ascii_letters + string.digits, k=8))

rabbitmq = RabbitMQ()
rabbitmq.start_connection()
mqtt = Subscriber(client_id, rabbitmq)
mqtt.start_connection()
mqtt.subscribe()

if __name__ == '__main__':
    while True:
        time.sleep(1)


