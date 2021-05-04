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

    def device_antecedent_measure(self, device_id, measure):
        if "SWITCH" not in device_id:
            key_pattern = "device:" + device_id
            if "WATERLEVEL" in device_id:
                max_measure = int(self.r.get(key_pattern + ":setting:max"))
                error_setting = int(self.r.get(key_pattern + ":setting:error"))
                relative_measure = float(measure) - float(error_setting)
                measure = str(round((1 - (relative_measure / float(max_measure))) * 100.0))
            elif "PHOTOCELL" in device_id or "SOILMOISTURE" in device_id:
                max_measure = 1024
                measure = str(round((int(measure) / max_measure) * 100.0))
            elif "AMMETER" in device_id:
                max_measure = int(self.r.get(key_pattern + ":setting:max"))
                measure = str(round((int(measure) / max_measure) * 100.0))
        return measure

    def device_evaluation(self, device_id, measure):
        output = Trigger("", device_id, "", [], "")
        try:
            key_pattern = "device:" + device_id
            if self.r.exists(key_pattern + ":userid") == 1:
                user_id = self.r.get("device:" + device_id + ":userid")
                output.user_id = user_id
                absolute_measure = measure
                measure = self.device_antecedent_measure(device_id, measure)
                output.measure = measure
                self.r.setex(key_pattern + ":measure", self.EXPIRATION, measure)
                self.r.setex(key_pattern + ":absolute_measure", self.EXPIRATION, absolute_measure)
                rules = []
                if "SWITCH" not in device_id:
                    output.type = "antecedent"
                    if self.r.exists(key_pattern + ":rules"):
                        rules = list(self.r.smembers(key_pattern + ":rules"))
                    output.rules = rules
                else:
                    output.type = "consequent"
                    output.rules = rules
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
