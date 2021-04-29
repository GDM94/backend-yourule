import redis
from os.path import dirname, join, abspath
import configparser
import json
from .dto.TriggerDTO import Trigger
from .dto.AntecedentEvaluationDTO import AntecedentEvaluation


class AntecedentServiceEvaluation(object):
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

    def antecedent_evaluation(self, trigger):
        output = AntecedentEvaluation(trigger["user_id"], [])
        try:
            for rule_id in trigger["rules"]:
                if self.r.exists("user:" + trigger["user_id"] + ":rule:" + rule_id + ":name") == 1:
                    key_pattern = "user:" + trigger["user_id"] + ":rule:" + rule_id + ":antecedent:" + trigger["device_id"]
                    evaluation = "false"
                    old_evaluation = self.r.get(key_pattern + ":evaluation")
                    condition = self.r.get(key_pattern + ":condition")
                    start_value = int(self.r.get(key_pattern + ":start_value"))
                    measure = int(trigger["measure"])
                    if condition == "between":
                        stop_value = int(self.r.get(key_pattern + ":stop_value"))
                        if start_value <= measure < stop_value:
                            evaluation = "true"
                    elif condition == ">":
                        if measure > start_value:
                            evaluation = "true"
                    elif condition == "<":
                        if measure < start_value:
                            evaluation = "true"
                    elif condition == "isteresi":
                        stop_value = int(self.r.get(key_pattern + ":stop_value"))
                        if measure <= start_value:
                            evaluation = "true"
                        if old_evaluation == "true" and measure <= stop_value:
                            evaluation = "true"
                    if evaluation != old_evaluation:
                        self.r.set(key_pattern + ":evaluation", evaluation)
                        output.rules.append(rule_id)
        except Exception as error:
            print(repr(error))
            return output
        else:
            return output
