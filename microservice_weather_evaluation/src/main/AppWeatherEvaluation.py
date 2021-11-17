import time
from app.WeatherServiceEvaluationImpl import WeatherServiceEvaluation
from app.RabbitMqClient import RabbitMQ
import random
import string
from configuration.config import read_config
from ruleapp.DBconnection.RedisConnectionImpl import RedisConnection

client_id = 'weather_trigger'.join(random.choices(string.ascii_letters + string.digits, k=8))

config = read_config()
redis = RedisConnection(config)
rabbitmq = RabbitMQ(client_id, config)
rabbitmq.start_connection()
service = WeatherServiceEvaluation(rabbitmq, redis, config)

if __name__ == '__main__':
    while True:
        service.weather_trigger()
        time.sleep(3)
