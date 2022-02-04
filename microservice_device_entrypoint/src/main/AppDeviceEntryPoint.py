from app.MQTTSubscriber import Subscriber
import time
import random
import string
from configuration.config import read_config

client_id = 'device_entrypoint'.join(random.choices(string.ascii_letters + string.digits, k=8))

config = read_config()

mqtt = Subscriber(config, client_id)
mqtt.start_connection()

if __name__ == '__main__':
    while True:
        time.sleep(1)




