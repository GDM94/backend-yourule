import time
from app.DeviceServiceEvaluationImpl import DeviceServiceEvaluation
from app.RabbitMqClient import RabbitMQ
import random
import string
from configuration.config import read_config
from ruleapp.DBconnection.RedisConnectionImpl import RedisConnection
from app.MQTTSubscriber import Subscriber

client_id = 'device_subscriber'.join(random.choices(string.ascii_letters + string.digits, k=8))

config = read_config()
redis = RedisConnection(config)
service = DeviceServiceEvaluation(redis)

mqtt = Subscriber(client_id)
mqtt.start_connection()

rabbitmq = RabbitMQ(client_id, service, config, mqtt)
rabbitmq.start_connection()
rabbitmq.subscribe()

if __name__ == '__main__':
    while True:
        time.sleep(1)
