import time
from configuration.config import read_config
import requests
from datetime import datetime

config = read_config()
backend_server = config.get("BACKEND", "ip")

if __name__ == '__main__':
    time.sleep(20)
    measure_time = datetime.now().strftime("%H:%M")
    while True:
        time.sleep(1)
        next_time = datetime.now().strftime("%H:%M")
        if measure_time != next_time:
            measure_time = next_time
            requests.get(backend_server)
