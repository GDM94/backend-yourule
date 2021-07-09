from app.RabbitMqClient import RabbitMQ
from app.RuleServiceEvaluationImpl import RuleServiceEvaluation
import time
import random
import string

client_id = random_client_id = 'rule_subscriber'.join(random.choices(string.ascii_letters + string.digits, k=8))
service = RuleServiceEvaluation()
rabbitmq = RabbitMQ(client_id, service)
rabbitmq.start_connection()
rabbitmq.subscribe()

if __name__ == '__main__':
    while True:
        time.sleep(1)
