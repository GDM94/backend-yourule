from app.MQTTSubscriber import Subscriber
from app.SwitchServiceEvaluationImpl import SwitchServiceEvaluation
from app.RabbitMqClient import RabbitMQ
import time
import random
import string

client_id = random_client_id = 'switch'.join(random.choices(string.ascii_letters + string.digits, k=8))

switch = SwitchServiceEvaluation()
mqtt = Subscriber(client_id, switch)
mqtt.start_connection()
rabbitmq = RabbitMQ(client_id, switch, mqtt)
rabbitmq.start_connection()
rabbitmq.subscribe()


if __name__ == '__main__':
    while True:
        time.sleep(1)
