import json
from ruleapp.Rule.RuleFunctions import RuleFunction


class RuleService(object):
    def __init__(self, mqtt_client, rabbitmq, config, redis):
        self.publish_rule = config.get("RABBITMQ", "publish_rule")
        self.r = redis
        self.mqtt_client = mqtt_client
        self.rabbitmq = rabbitmq
        self.rule_functions = RuleFunction(redis)

    def create_new_rule(self, user_id, rule_name):
        return self.rule_functions.create_rule(user_id, rule_name)

    def get_user_rules(self, user_id):
        return self.rule_functions.get_user_rules(user_id)

    def update_rule_name(self, user_id, rule_id, name):
        return self.rule_functions.update_rule_name(user_id, rule_id, name)

    def add_rule_antecedent(self, user_id, rule_id, device_id, antecedent_json):
        return self.rule_functions.add_rule_antecedent(user_id, rule_id, device_id, antecedent_json)

    def add_rule_consequent(self, user_id, rule_id, device_id, consequent_json):
        return self.rule_functions.add_rule_consequent(user_id, rule_id, device_id, consequent_json)

    def update_rule_antecedent(self, user_id, rule_id, device_id, antecedent_json):
        return self.rule_functions.update_rule_antecedent(user_id, rule_id, device_id, antecedent_json)

    def update_rule_consequent(self, user_id, rule_id, device_id, consequent_json):
        return self.rule_functions.update_rule_consequent(user_id, rule_id, device_id, consequent_json)

    def delete_rule(self, user_id, rule_id):
        return self.rule_functions.delete_rule(user_id, rule_id)

    def delete_antecedent(self, user_id, rule_id, device_id):
        try:
            output = self.rule_functions.delete_rule_antecedent(user_id, rule_id, device_id)
            if output != "error":
                # trigger rule evaluation
                trigger_message = {"user_id": user_id, "rules": [rule_id]}
                payload = json.dumps(trigger_message)
                self.rabbitmq.publish(self.publish_rule, payload)
            return output
        except Exception as error:
            print(repr(error))
            return "error"

    def delete_consequent(self, user_id, rule_id, device_id):
        try:
            output = self.rule_functions.delete_rule_consequent(user_id, rule_id, device_id)
            if output != "error":
                # trigger device off
                self.mqtt_client.publish(device_id, "off/0")
            return output
        except Exception as error:
            print(repr(error))
            return "error"

    def get_rule_by_id(self, user_id, rule_id):
        return self.rule_functions.get_rule(user_id, rule_id)

    def get_rule_antecedents(self, user_id, rule_id):
        return self.rule_functions.get_rule_antecedents(user_id, rule_id)

    def get_antecedent(self, user_id, rule_id, device_id):
        return self.rule_functions.get_rule_antecedent(user_id, rule_id, device_id)

    def get_rule_consequents(self, user_id, rule_id):
        return self.rule_functions.get_rule_consequents(user_id, rule_id)

    def get_consequent(self, user_id, rule_id, device_id):
        return self.rule_functions.get_rule_consequent(user_id, rule_id, device_id)

    def get_device_rules(self, user_id, device_id):
        try:
            output = list(self.r.smembers("device:" + device_id + ":rules"))
        except Exception as error:
            print(repr(error))
            return "error"
        else:
            return output

