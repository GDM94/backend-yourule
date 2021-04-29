import time
from app.LastTimeOnEvaluationImpl import LastTimeOnEvaluation
from app.RabbitMqClient import RabbitMQ
import random
import string

client_id = random_client_id = 'last_timeon'.join(random.choices(string.ascii_letters + string.digits, k=8))
rabbitmq = RabbitMQ(client_id)
rabbitmq.start_connection()
service = LastTimeOnEvaluation(rabbitmq)

if __name__ == '__main__':
    while True:
        service.last_value_on_trigger()
        time.sleep(3)
