import time
from app.DeviceServiceEvaluationImpl import DeviceServiceEvaluation
from app.RabbitMqClient import RabbitMQ
import random
import string
from appconfig.Config import read_config

client_id = random_client_id = 'device_subscriber'.join(random.choices(string.ascii_letters + string.digits, k=8))

service = DeviceServiceEvaluation()
rabbitmq = RabbitMQ(client_id, service)
rabbitmq.start_connection()
rabbitmq.subscribe()

if __name__ == '__main__':
    while True:
        time.sleep(1)
