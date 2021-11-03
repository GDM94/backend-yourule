import time
from app.TimerServiceEvaluationImpl import TimerServiceEvaluation
from app.RabbitMqClient import RabbitMQ
import random
import string
from configuration.config import read_config
from ruleapp.DBconnection.RedisConnectionImpl import RedisConnection

client_id = 'timer_trigger'.join(random.choices(string.ascii_letters + string.digits, k=8))

config = read_config()
redis = RedisConnection(config)
rabbitmq = RabbitMQ(client_id, config)
rabbitmq.start_connection()
service = TimerServiceEvaluation(rabbitmq, redis)

if __name__ == '__main__':
    while True:
        service.timer_trigger()
        time.sleep(3)
