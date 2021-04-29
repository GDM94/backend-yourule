from app.MQTTSubscriber import Subscriber
from app.ConsequentServiceEvaluationImpl import ConsequentServiceEvaluation
from app.RabbitMqClient import RabbitMQ
import time
import random
import string

client_id = random_client_id = 'consequent'.join(random.choices(string.ascii_letters + string.digits, k=8))

consequent = ConsequentServiceEvaluation()
mqtt = Subscriber(client_id, consequent)
mqtt.start_connection()
rabbitmq = RabbitMQ(client_id, consequent, mqtt)
rabbitmq.start_connection()
rabbitmq.subscribe()


if __name__ == '__main__':
    while True:
        time.sleep(1)
