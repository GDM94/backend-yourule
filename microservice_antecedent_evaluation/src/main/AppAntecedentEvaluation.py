import time
from app.RabbitMqClient import RabbitMQ
import random
import string
from configuration.config import read_config


client_id = 'antecedent'.join(random.choices(string.ascii_letters + string.digits, k=8))

config = read_config()
rabbitmq = RabbitMQ(client_id, config)
rabbitmq.start_connection()
rabbitmq.subscribe()

if __name__ == '__main__':
    while True:
        time.sleep(1)
