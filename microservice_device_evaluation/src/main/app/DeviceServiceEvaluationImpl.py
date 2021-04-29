import redis
from os.path import dirname, join, abspath
import configparser
from .dto.TriggerDTO import Trigger
import json
from datetime import datetime


class DeviceServiceEvaluation(object):
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

    def device_evaluation(self, device_id, measure):
        output = Trigger("", "", "", [], "")
        try:
            key_pattern = "device:" + device_id
            if self.r.exists(key_pattern + ":userid") == 1:
                user_id = self.r.get("device:" + device_id + ":userid")
                device_prefix = device_id.split("-")[0]
                if device_prefix == "WATERLEVEL":
                    max_measure = int(self.r.get(key_pattern + ":setting:max"))
                    error_setting = int(self.r.get(key_pattern + ":setting:error"))
                    relative_measure = float(measure) - float(error_setting)
                    measure = str(round((1 - (relative_measure / float(max_measure))) * 100.0))
                elif device_prefix == "PHOTOCELL":
                    max_measure = 1024
                    measure = str(round((int(measure) / max_measure) * 100.0))
                elif device_prefix == "SOILMOISTURE":
                    max_measure = 1025
                    measure = str(round((int(measure) / max_measure) * 100.0))
                self.r.setex(key_pattern + ":measure", self.EXPIRATION, measure)
                if device_prefix != "SWITCH":
                    if self.r.exists(key_pattern + ":rules"):
                        rules = list(self.r.smembers(key_pattern + ":rules"))
                    else:
                        rules = []
                    if len(rules) > 0:
                        output = Trigger(user_id, device_id, measure, rules, "antecedent")
                else:
                    output = Trigger(user_id, device_id, measure, [], "consequent")
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    if measure == "on":
                        self.r.set(key_pattern+":last_on", timestamp)
                    else:
                        self.r.set(key_pattern+":last_off", timestamp)

        except Exception as error:
            print(repr(error))
            return output
        else:
            return output
