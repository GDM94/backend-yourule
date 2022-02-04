import time
from configuration.config import read_config
import requests

config = read_config()
backend_server = config.get("BACKEND", "ip")

if __name__ == '__main__':
    while True:
        requests.get(backend_server)
        time.sleep(10)

