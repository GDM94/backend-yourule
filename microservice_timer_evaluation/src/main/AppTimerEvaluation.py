import time
from app.TimerServiceEvaluationImpl import TimerServiceEvaluation
from app.RabbitMqClient import RabbitMQ
import random
import string

client_id = random_client_id = 'timer_trigger'.join(random.choices(string.ascii_letters + string.digits, k=8))
rabbitmq = RabbitMQ(client_id)
rabbitmq.start_connection()
service = TimerServiceEvaluation(rabbitmq)

if __name__ == '__main__':
    while True:
        service.timer_trigger()
        time.sleep(3)
