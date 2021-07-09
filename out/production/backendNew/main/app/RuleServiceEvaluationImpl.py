import redis
from os.path import dirname, join, abspath
import configparser
import json
from datetime import datetime


class RuleServiceEvaluation(object):
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

    def check_antecedent_evaluation(self, antecedent_keys):
        new_evaluation = "true"
        for key in antecedent_keys:
            evaluation = self.r.get(key)
            if evaluation == "false":
                new_evaluation = "false"
                break
        if new_evaluation == "true":
            for key in antecedent_keys:
                antecedent_device_id = key.split(":")[-2]
                if "timer" not in antecedent_device_id:
                    if self.r.exists("device:" + antecedent_device_id + ":measure") == 0:
                        new_evaluation = "false"
                        break
        return new_evaluation

    def update_evaluation_timestamp(self, pattern_key, evaluation):
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        if evaluation == "true":
            self.r.set(pattern_key+":last_false", timestamp)
        else:
            self.r.set(pattern_key+":last_true", timestamp)

    def rule_evaluation(self, user_id, rule_id):
        try:
            output = {"user_id": "", "rule_id": ""}
            pattern_key = "user:" + user_id + ":rule:" + rule_id
            if self.r.exists(pattern_key + ":name") == 1:
                old_evaluation = self.r.get(pattern_key + ":evaluation")
                antecedent_keys = self.r.scan(0, pattern_key + ":antecedent:*:evaluation", 1000)[1]
                new_evaluation = "false"
                if len(antecedent_keys) > 0:
                    new_evaluation = self.check_antecedent_evaluation(antecedent_keys)
                if old_evaluation != new_evaluation:
                    self.r.set(pattern_key + ":evaluation", new_evaluation)
                    self.update_evaluation_timestamp(pattern_key, new_evaluation)
                    output["user_id"] = user_id
                    output["rule_id"] = rule_id
        except Exception as error:
            print(repr(error))
            return output
        else:
            return output
