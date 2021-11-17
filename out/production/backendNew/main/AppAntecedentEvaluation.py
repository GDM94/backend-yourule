import time
from app.AntecedentServiceEvaluationImpl import AntecedentServiceEvaluation
from app.RabbitMqClient import RabbitMQ
import random
import string
from configuration.config import read_config
from ruleapp.DBconnection.RedisConnectionImpl import RedisConnection


client_id = 'antecedent'.join(random.choices(string.ascii_letters + string.digits, k=8))

config = read_config()
redis = RedisConnection(config)
service = AntecedentServiceEvaluation(redis)
rabbitmq = RabbitMQ(client_id, service, config)
rabbitmq.start_connection()
rabbitmq.subscribe()

if __name__ == '__main__':
    while True:
        time.sleep(1)
