import time
from app.AntecedentServiceEvaluationImpl import AntecedentServiceEvaluation
from app.RabbitMqClient import RabbitMQ
import random
import string

client_id = random_client_id = 'antecedent'.join(random.choices(string.ascii_letters + string.digits, k=8))

service = AntecedentServiceEvaluation()
rabbitmq = RabbitMQ(client_id, service)
rabbitmq.start_connection()
rabbitmq.subscribe()

if __name__ == '__main__':
    while True:
        time.sleep(1)
