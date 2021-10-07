from app.MQTTSubscriber import Subscriber
from app.SwitchServiceEvaluationImpl import SwitchServiceEvaluation
from app.RabbitMqClient import RabbitMQ
import time
import random
import string
from configuration.config import read_config
from ruleapp.DBconnection.RedisConnectionImpl import RedisConnection

client_id = random_client_id = 'switch'.join(random.choices(string.ascii_letters + string.digits, k=8))

config = read_config()
redis = RedisConnection(config)
switch = SwitchServiceEvaluation(redis)
mqtt = Subscriber(client_id, switch)
mqtt.start_connection()
rabbitmq = RabbitMQ(client_id, switch, mqtt, config)
rabbitmq.start_connection()
rabbitmq.subscribe()


if __name__ == '__main__':
    while True:
        time.sleep(1)
