from app.MQTTSubscriber import Subscriber
from app.ConsequentServiceEvaluationImpl import ConsequentServiceEvaluation
from app.RabbitMqClient import RabbitMQ
import time
import random
import string
from configuration.config import read_config
from ruleapp.DBconnection.RedisConnectionImpl import RedisConnection

client_id = 'consequent'.join(random.choices(string.ascii_letters + string.digits, k=8))

config = read_config()
redis = RedisConnection(config)

mqtt = Subscriber(client_id, config)
mqtt.start_connection()

consequent = ConsequentServiceEvaluation(config, redis)

rabbitmq = RabbitMQ(client_id, consequent, mqtt, config)
rabbitmq.start_connection()
rabbitmq.subscribe()


if __name__ == '__main__':
    while True:
        time.sleep(1)
