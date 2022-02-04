import time
from configuration.config import read_config
import requests

config = read_config()
backend_server = config.get("BACKEND", "ip")

if __name__ == '__main__':
    time.sleep(10)
    while True:
        time.sleep(10)
        requests.get(backend_server)

