import time
from app.LastTimeOnEvaluationImpl import LastTimeOnEvaluation
from app.RabbitMqClient import RabbitMQ
import random
import string
from configuration.config import read_config
from ruleapp.DBconnection.RedisConnectionImpl import RedisConnection

client_id = 'last_timeon'.join(random.choices(string.ascii_letters + string.digits, k=8))
config = read_config()
redis = RedisConnection(config)
rabbitmq = RabbitMQ(client_id, config)
rabbitmq.start_connection()
service = LastTimeOnEvaluation(rabbitmq, redis)

if __name__ == '__main__':
    while True:
        service.last_value_on_trigger()
        time.sleep(5)
