import json
from ruleapp.Devices.Timer.TimerAntecedentFunctions import TimerAntecedentFunction


class TimerServiceEvaluation(object):
    def __init__(self, rabbitmq, redis):
        self.r = redis
        self.rabbitmq = rabbitmq
        self.timer_antecedent_functions = TimerAntecedentFunction(redis)

    def get_all_users(self):
        users_keys = self.r.scan("profile:*:user_id")
        user_id_list = []
        for user_key in users_keys:
            user_id = self.r.get(user_key)
            user_id_list.append(user_id)
        return user_id_list

    def get_rules_with_timer(self, user_id, device_id):
        rules_id_list = self.r.lrange("user:" + user_id + ":rules")
        output = []
        for rule_id in rules_id_list:
            key_pattern = "user:" + user_id + ":rule:" + rule_id
            device_antecedents = self.r.lrange(key_pattern + ":device_antecedents")
            if device_id in device_antecedents:
                output.append(rule_id)
        return output

    def timer_trigger(self):
        user_id_list = self.get_all_users()
        for user_id in user_id_list:
            device_id = "timer-"+user_id
            output = {"user_id": user_id, "rules": []}
            rule_id_list = self.get_rules_with_timer(user_id, device_id)
            for rule_id in rule_id_list:
                trigger = self.timer_antecedent_functions.antecedent_evaluation(user_id, device_id, rule_id)
                if trigger == "true":
                    output["rules"].append(rule_id)
            if len(output["rules"]) > 0:
                payload = json.dumps(output)
                self.rabbitmq.publish(payload)
