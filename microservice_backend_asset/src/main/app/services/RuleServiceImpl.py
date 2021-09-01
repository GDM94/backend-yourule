from ..dto.AntecedentDTO import Antecedent
from ..dto.ConsequentDTO import Consequent
from ..dto.RuleDTO import Rule
import json
from datetime import datetime
from ..dto.Rule.RuleDTO import Rule
from ..dto.Rule.RuleFunctions import RuleFunction


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
        try:
            return self.rule_functions.get_rule(user_id, rule_id)
        except Exception as error:
            print(repr(error))
            return "error"

    def get_rule_antecedents(self, user_id, rule_id):
        key_pattern = "user:" + user_id + ":rule:" + rule_id
        antecedent_keys = self.r.scan(key_pattern + ":antecedent:*:start_value")
        antecedent_list = []
        if len(antecedent_keys) > 0:
            for key in antecedent_keys:
                device_id = key.split(":")[-2]
                antecedent = self.get_antecedent(user_id, rule_id, device_id)
                antecedent_list.append(antecedent)
        antecedent_list.sort(key=lambda device: int(device.order))
        return antecedent_list

    def get_antecedent(self, user_id, rule_id, device_id):
        key_pattern = "user:" + user_id + ":rule:" + rule_id + ":antecedent:" + device_id
        start_value = self.r.get(key_pattern + ":start_value")
        stop_value = self.r.get(key_pattern + ":stop_value")
        condition = self.r.get(key_pattern + ":condition")
        evaluation = self.r.get(key_pattern + ":evaluation")
        measure = self.r.get(key_pattern + ":measure")
        order = self.r.get(key_pattern + ":order")
        device_name = self.r.get("device:" + device_id + ":name")
        value = "null"
        if "SWITCH" in device_id:
            if self.r.exists("device:" + device_id + ":measure"):
                value = self.r.get("device:" + device_id + ":last_on")
        else:
            if self.r.exists("device:" + device_id + ":absolute_measure"):
                absolute_measure = self.r.get("device:" + device_id + ":absolute_measure")
                value = self.device_antecedent_measure(device_id, absolute_measure)
        return Antecedent(device_id, device_name, start_value, stop_value, condition, evaluation, measure, value, order)

    def device_antecedent_measure(self, device_id, measure):
        if "SWITCH" not in device_id:
            if measure != "init":
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

    def get_rule_consequents(self, user_id, rule_id):
        key_pattern = "user:" + user_id + ":rule:" + rule_id
        consequent_keys = self.r.scan(key_pattern + ":consequent:*:if_value")
        consequent_list = []
        if len(consequent_keys) > 0:
            for key in consequent_keys:
                k = key.split(":")
                device_id = k[-2]
                consequent = self.get_consequent(user_id, rule_id, device_id)
                consequent_list.append(consequent)
        consequent_list.sort(key=lambda device: int(device.order))
        return consequent_list

    def get_consequent(self, user_id, rule_id, device_id):
        key_pattern = "user:" + user_id + ":rule:" + rule_id
        if_value = self.r.get(key_pattern + ":consequent:" + device_id + ":if_value")
        else_value = self.r.get(key_pattern + ":consequent:" + device_id + ":else_value")
        order = self.r.get(key_pattern + ":consequent:" + device_id + ":order")
        delay = self.r.get(key_pattern + ":consequent:" + device_id + ":delay")
        device_name = self.r.get("device:" + device_id + ":name")
        automatic = self.r.get("device:" + device_id + ":automatic")
        measure = "null"
        if self.r.exists("device:" + device_id + ":measure"):
            measure = self.r.get("device:" + device_id + ":measure")
        return Consequent(device_id, device_name, if_value, else_value, automatic, measure, order, delay)

    def get_device_rules(self, user_id, device_id):
        try:
            output = list(self.r.smembers("device:" + device_id + ":rules"))
        except Exception as error:
            print(repr(error))
            return "error"
        else:
            return output

