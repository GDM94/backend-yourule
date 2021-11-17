from app.RabbitMqClient import RabbitMQ
from app.RuleServiceEvaluationImpl import RuleServiceEvaluation
import time
import random
import string
from configuration.config import read_config
from ruleapp.DBconnection.RedisConnectionImpl import RedisConnection

client_id = 'rule_subscriber'.join(random.choices(string.ascii_letters + string.digits, k=8))
config = read_config()
redis = RedisConnection(config)
service = RuleServiceEvaluation(redis)
rabbitmq = RabbitMQ(client_id, service, config)
rabbitmq.start_connection()
rabbitmq.subscribe()

if __name__ == '__main__':
    while True:
        time.sleep(1)
