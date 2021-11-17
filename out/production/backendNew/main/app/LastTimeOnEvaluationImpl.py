import json
from ruleapp.Devices.Switch.SwitchAntecedentFunctions import SwitchAntecedentFunction


class LastTimeOnEvaluation(object):
    def __init__(self, rabbitmq, redis):
        self.r = redis
        self.rabbitmq = rabbitmq
        self.switch_antecedent_function = SwitchAntecedentFunction(redis)

    def get_all_users(self):
        users_keys = self.r.scan("profile:*:user_id")
        user_id_list = []
        for user_key in users_keys:
            user_id = self.r.get(user_key)
            user_id_list.append(user_id)
        return user_id_list

    def get_rules_with_switch(self, user_id):
        rules_id_list = self.r.lrange("user:" + user_id + ":rules")
        output = set()
        for rule_id in rules_id_list:
            key_pattern = "user:" + user_id + ":rule:" + rule_id
            device_antecedents = self.r.lrange(key_pattern + ":device_antecedents")
            for device_id in device_antecedents:
                if "SWITCH" in device_id:
                    trigger = self.switch_antecedent_function.antecedent_evaluation(user_id, device_id, rule_id)
                    if trigger == "true":
                        output.add(rule_id)
        output_list = list(output)
        return output_list

    def last_value_on_trigger(self):
        user_id_list = self.get_all_users()
        for user_id in user_id_list:
            output = {"user_id": user_id, "rules": []}
            rules_id_list = self.get_rules_with_switch(user_id)
            if len(rules_id_list) > 0:
                output["rules"] = rules_id_list
                self.rabbitmq.publish(json.dumps(output))
