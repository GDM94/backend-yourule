import smtplib
from email.mime.text import MIMEText
import redis
from os.path import dirname, join, abspath
import configparser
import json


class SwitchServiceEvaluation(object):
    def __init__(self):
        config = self.read_config()
        HOST = config.get("REDIS", "host")
        PORT = config.get("REDIS", "port")
        self.EXPIRATION = config.get("REDIS", "expiration")
        self.r = redis.Redis(host=HOST, port=PORT, decode_responses=True)

    def read_config(self):
        d = dirname(dirname(dirname(abspath(__file__))))
        config_path = join(d, 'properties', 'app-config.ini')
        config = configparser.ConfigParser()
        config.read(config_path)
        return config

    def switch_evaluation(self, payload):
        output = {"device_id": "", "measure": ""}
        try:
            trigger = json.loads(payload)
            user_id = str(trigger["user_id"])
            device_id = str(trigger["device_id"])
            measure = str(trigger["measure"])
            key_pattern = "device:" + device_id
            automatic = self.r.get(key_pattern + ":automatic")
            if automatic == "true":
                rules = list(self.r.smembers(key_pattern + ":rules"))
                consequent_evaluation = "false"
                for rule in rules:
                    if self.r.get("user:" + user_id + ":rule:" + rule + ":evaluation") == "true":
                        consequent_evaluation = "true"
                        break
                status = "off"
                if consequent_evaluation == "true":
                    status = "on"
            else:
                status = self.r.get(key_pattern+":manual_measure")
            if measure != status:
                output["device_id"] = device_id
                output["measure"] = status
        except Exception as error:
            print(repr(error))
            return output
        else:
            return output
