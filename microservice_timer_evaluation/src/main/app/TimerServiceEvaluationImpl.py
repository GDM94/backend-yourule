import json
from datetime import datetime
from ruleapp.Devices.Timer.TimerAntecedentFunctions import TimerAntecedentFunction


class TimerServiceEvaluation(object):
    def __init__(self, mqtt_client, redis):
        self.r = redis
        self.mqtt_client = mqtt_client
        self.timer_antecedent_functions = TimerAntecedentFunction(redis)

    def get_all_users(self):
        users_keys = self.r.scan("user:name:*:id")
        user_id_list = []
        for user_key in users_keys:
            user_id = self.r.get(user_key)
            user_id_list.append(user_id)
        return user_id_list

    def get_rules_with_timer(self, user_id):
        timer_id = "timer" + user_id
        rules_keys = self.r.scan("user:" + user_id + ":rule:*:antecedent:" + timer_id + ":start_value")
        rule_id_list = []
        for rule_key in rules_keys:
            rule_id = rule_key.split(":")[3]
            rule_id_list.append(rule_id)
        return rule_id_list

    def timer_trigger(self):
        user_id_list = self.get_all_users()
        for user_id in user_id_list:
            output = {"user_id": user_id, "rules": []}
            rule_id_list = self.get_rules_with_timer(user_id)
            for rule_id in rule_id_list:
                trigger = self.timer_antecedent_functions.antecedent_evaluation(user_id, rule_id)
                if trigger == "true":
                    output["rules"].append(rule_id)
            if len(output["rules"]) > 0:
                payload = json.dumps(output)
                self.mqtt_client.publish(payload)
