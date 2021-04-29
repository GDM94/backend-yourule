import redis
from os.path import dirname, join, abspath
import configparser
import json
from datetime import datetime
from .dto.AntecedentEvaluationDTO import AntecedentEvaluation


class TimerServiceEvaluation(object):
    def __init__(self, mqtt_client):
        config = self.read_config()
        HOST = config.get("REDIS", "host")
        PORT = config.get("REDIS", "port")
        self.EXPIRATION = config.get("REDIS", "expiration")
        self.r = redis.Redis(host=HOST, port=PORT, decode_responses=True)
        self.mqtt_client = mqtt_client

    def read_config(self):
        d = dirname(dirname(dirname(abspath(__file__))))
        config_path = join(d, 'properties', 'app-config.ini')
        config = configparser.ConfigParser()
        config.read(config_path)
        return config

    def get_all_users(self):
        users_keys = self.r.scan(0, "user:name:*:id", 1000)[1]
        user_id_list = []
        for user_key in users_keys:
            user_id = self.r.get(user_key)
            user_id_list.append(user_id)
        return user_id_list

    def get_rules_with_timer(self, user_id):
        timer_id = "timer" + user_id
        rules_keys = self.r.scan(0, "user:" + user_id + ":rule:*:antecedent:" + timer_id + ":start_value", 1000)[1]
        rule_id_list = []
        for rule_key in rules_keys:
            rule_id = rule_key.split(":")[3]
            rule_id_list.append(rule_id)
        return rule_id_list

    def timer_trigger(self):
        user_id_list = self.get_all_users()
        for user_id in user_id_list:
            output = AntecedentEvaluation(user_id, [])
            rule_id_list = self.get_rules_with_timer(user_id)
            for rule_id in rule_id_list:
                trigger = self.timer_evaluation(user_id, rule_id)
                if trigger:
                    output.rules.append(rule_id)
            if len(output.rules) > 0:
                payload = json.dumps(output, default=lambda o: o.__dict__)
                self.mqtt_client.publish(payload)

    def timer_evaluation(self, user_id, rule_id):
        trigger = False
        timer_id = "timer" + user_id
        pattern_key = "user:" + user_id + ":rule:" + rule_id + ":antecedent:" + timer_id
        evaluation = "false"
        old_evaluation = self.r.get(pattern_key + ":evaluation")
        start_value_str = self.r.get(pattern_key + ":start_value")
        start_value = datetime.strptime(start_value_str, '%H:%M').time()
        measure_str = datetime.now().strftime("%H:%M")
        measure_now = datetime.strptime(measure_str, '%H:%M').time()
        condition = self.r.get(pattern_key + ":condition")
        if condition == "between":
            stop_value_str = self.r.get(pattern_key + ":stop_value")
            stop_value = datetime.strptime(stop_value_str, '%H:%M').time()
            if start_value <= measure_now < stop_value:
                evaluation = "true"
        elif condition == ">":
            if measure_now > start_value:
                evaluation = "true"
        elif condition == "<":
            if measure_now < start_value:
                evaluation = "true"
        if evaluation != old_evaluation:
            self.r.set(pattern_key + ":evaluation", evaluation)
            trigger = True
        return trigger
