from app.RabbitMqClient import RabbitMQ
from app.MQTTSubscriber import Subscriber
import time
import random
import string
from configuration.config import read_config
from ruleapp.DBconnection.RedisConnectionImpl import RedisConnection

client_id = 'device_entrypoint'.join(random.choices(string.ascii_letters + string.digits, k=8))

config = read_config()
redis = RedisConnection(config)

rabbitmq = RabbitMQ(config, client_id)
rabbitmq.start_connection()

mqtt = Subscriber(config, client_id, rabbitmq, redis)
mqtt.start_connection()
mqtt.subscribe()

if __name__ == '__main__':
    while True:
        time.sleep(1)


