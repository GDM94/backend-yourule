from app.MQTTSubscriber import Subscriber
from app.ConsequentServiceEvaluationImpl import ConsequentServiceEvaluation
from app.RabbitMqClient import RabbitMQ
import time
import random
import string

client_id = random_client_id = 'consequent'.join(random.choices(string.ascii_letters + string.digits, k=8))


mqtt = Subscriber(client_id)
mqtt.start_connection()
consequent = ConsequentServiceEvaluation()
rabbitmq = RabbitMQ(client_id, consequent, mqtt)
rabbitmq.start_connection()
rabbitmq.subscribe()


if __name__ == '__main__':
    while True:
        time.sleep(1)
