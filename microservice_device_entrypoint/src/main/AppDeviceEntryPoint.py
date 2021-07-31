from app.RabbitMqClient import RabbitMQ
from app.MQTTSubscriber import Subscriber
import time
import random
import string
from configuration.config import read_config
from app.RedisConnectionImpl import RedisConnection
from app.DeviceInitializationImpl import DeviceInitialization
from app.MQTTSubscriberInitialization import SubscriberInitialization

client_id = 'device_entrypoint'.join(random.choices(string.ascii_letters + string.digits, k=8))
client_id_init = 'device_initialization'.join(random.choices(string.ascii_letters + string.digits, k=8))

config = read_config()
redis = RedisConnection(config)
rabbitmq = RabbitMQ(config)
rabbitmq.start_connection()

mqtt = Subscriber(config, client_id, rabbitmq)
mqtt.start_connection()
mqtt.subscribe()

service = DeviceInitialization(redis)
mqtt_initialization = SubscriberInitialization(config, client_id_init, service)
mqtt_initialization.start_connection()
mqtt_initialization.subscribe()

if __name__ == '__main__':
    while True:
        time.sleep(1)


