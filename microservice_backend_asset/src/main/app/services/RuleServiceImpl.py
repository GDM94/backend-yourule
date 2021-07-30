from ..dto.AntecedentDTO import Antecedent
from ..dto.ConsequentDTO import Consequent
from ..dto.RuleDTO import Rule
import json
from datetime import datetime


class RuleService(object):
    def __init__(self, mqtt_client, rabbitmq, config, redis):
        self.publish_rule = config.get("RABBITMQ", "publish_rule")
        self.r = redis
        self.mqtt_client = mqtt_client
        self.rabbitmq = rabbitmq

    def create_new_rule(self, user_id, rule_name):
        try:
            # set rule Id
            rule_id = str(self.r.incr("user:" + user_id + ":rule:counter"))
            key_pattern = "user:" + user_id + ":rule:" + rule_id
            # set rule name
            self.r.set(key_pattern + ":name", rule_name)
            self.r.set(key_pattern + ":evaluation", "false")
            timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            self.r.set(key_pattern + ":last_true", "-")
            self.r.set(key_pattern + ":last_false", timestamp)
            self.r.set(key_pattern + ":registration_date", timestamp)
        except Exception as error:
            print(repr(error))
            return "error"
        else:
            return rule_id

    def set_rule(self, user_id, rule_body):
        rule_id = str(rule_body["id"])
        rule_name = rule_body["name"]
        output = "added"
        output_name = self.set_new_name(user_id, rule_id, rule_name)
        if output_name == "error":
            output = "error"
        antecedent_list = rule_body["antecedent"]
        consequent_list = rule_body["consequent"]
        for antecedent in antecedent_list:
            new_antecedent = Antecedent(antecedent["device_id"], antecedent["name"], antecedent["start_value"],
                                        antecedent["stop_value"], antecedent["condition"], "false",
                                        antecedent["measure"], antecedent["value"])
            output_antecedent = self.set_new_antecedent(user_id, rule_id, new_antecedent)
            if output_antecedent == "error":
                output = "error"
        for consequent in consequent_list:
            new_consequent = Consequent(consequent["device_id"], consequent["name"], "on", "off",
                                        consequent["automatic"], consequent["measure"], consequent["order"],
                                        consequent["delay"])
            output_consequent = self.set_new_consequent(user_id, rule_id, new_consequent)
            if output_consequent == "error":
                output = "error"
        return output

    def set_new_name(self, user_id, rule_id, name):
        try:
            self.r.set("user:" + user_id + ":rule:" + rule_id + ":name", name)
        except Exception as error:
            print(repr(error))
            return "error"
        else:
            return "ok"

    def set_new_antecedent(self, user_id, rule_id, antecedent):
        try:
            self.r.sadd("device:" + antecedent.device_id + ":rules", rule_id)
            key_pattern = "user:" + user_id + ":rule:" + rule_id + ":antecedent:" + antecedent.device_id
            self.r.set(key_pattern + ":start_value", antecedent.start_value)
            self.r.set(key_pattern + ":stop_value", antecedent.stop_value)
            self.r.set(key_pattern + ":condition", antecedent.condition)
            self.r.set(key_pattern + ":measure", antecedent.measure)
            if self.r.exists(key_pattern + ":evaluation") == 0:
                self.r.set(key_pattern + ":evaluation", "init")
        except Exception as error:
            print(repr(error))
            return "error"
        else:
            return "added"

    def set_new_consequent(self, user_id, rule_id, consequent):
        try:
            self.r.sadd("device:" + consequent.device_id + ":rules", rule_id)
            key_pattern = "user:" + user_id + ":rule:" + rule_id + ":consequent:" + consequent.device_id
            self.r.set(key_pattern + ":if_value", consequent.if_value)
            self.r.set(key_pattern + ":else_value", consequent.else_value)
            self.r.set(key_pattern + ":order", consequent.order)
            self.r.set(key_pattern + ":delay", consequent.delay)
        except Exception as error:
            print(repr(error))
            return "error"
        else:
            return "added"

    def delete_rule(self, user_id, rule_id):
        try:
            key_pattern = "user:" + user_id + ":rule:" + rule_id
            if self.r.exists(key_pattern + ":name") == 1:
                # delete rule name
                self.r.delete(key_pattern + ":name")
                self.r.delete(key_pattern + ":evaluation")
                self.r.delete(key_pattern + ":last_true")
                self.r.delete(key_pattern + ":last_false")
                self.r.delete(key_pattern + ":registration_date")
                # delete rule antecedents
                antecedent_keys = self.r.scan(key_pattern + ":antecedent:*:start_value")
                if len(antecedent_keys) > 0:
                    for key in antecedent_keys:
                        k = key.split(":")
                        device_id = k[-2]
                        self.delete_antecedent(user_id, rule_id, device_id)
                # delete rule consequent
                consequent_keys = self.r.scan(key_pattern + ":consequent:*:if_value")
                if len(consequent_keys) > 0:
                    for key in consequent_keys:
                        k = key.split(":")
                        device_id = k[-2]
                        self.delete_consequent(user_id, rule_id, device_id)
        except Exception as error:
            print(repr(error))
            return "error"
        else:
            return "rule with id {} is succesfully deleted".format(rule_id)

    def delete_antecedent(self, user_id, rule_id, device_id):
        try:
            key_pattern = "user:" + user_id + ":rule:" + rule_id + ":antecedent:" + device_id
            # delete antecedent
            self.r.srem("device:" + device_id + ":rules", rule_id)
            self.r.delete(key_pattern + ":start_value")
            self.r.delete(key_pattern + ":stop_value")
            self.r.delete(key_pattern + ":condition")
            self.r.delete(key_pattern + ":evaluation")
            self.r.delete(key_pattern + ":measure")
            # trigger rule evaluation
            trigger_message = {"user_id": user_id, "rules": [rule_id]}
            payload = json.dumps(trigger_message)
            self.rabbitmq.publish(self.publish_rule, payload)
        except Exception as error:
            print(repr(error))
            return "error"
        else:
            return "deleted"

    def delete_consequent(self, user_id, rule_id, device_id):
        try:
            # delete consequent
            self.r.srem("device:" + device_id + ":rules", rule_id)
            key_pattern = "user:" + user_id + ":rule:" + rule_id + ":consequent:" + device_id
            self.r.delete(key_pattern + ":if_value")
            self.r.delete(key_pattern + ":else_value")
            self.r.delete(key_pattern + ":order")
            self.r.delete(key_pattern + ":delay")
            # trigger device off
            self.mqtt_client.publish(device_id, "off/0")
        except Exception as error:
            print(repr(error))
            return "error"
        else:
            return "deleted"

    def get_rule_by_id(self, user_id, rule_id):
        try:
            key_pattern = "user:" + user_id + ":rule:" + rule_id
            if self.r.exists(key_pattern + ":name") == 1:
                # get rule name
                rule_name = self.r.get(key_pattern + ":name")
                rule_evaluation = self.r.get(key_pattern + ":evaluation")
                timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                if rule_evaluation == "false":
                    last_true = self.r.get(key_pattern + ":last_true")
                    last_false = timestamp
                else:
                    last_true = timestamp
                    last_false = self.r.get(key_pattern + ":last_false")
                # get rule antecedents
                antecedent_keys = self.r.scan(key_pattern + ":antecedent:*:start_value")
                antecedent_list = []
                if len(antecedent_keys) > 0:
                    for key in antecedent_keys:
                        device_id = key.split(":")[-2]
                        antecedent = self.get_antecedent(user_id, rule_id, device_id)
                        antecedent_list.append(antecedent)
                # get rule consequent
                consequent_keys = self.r.scan(key_pattern + ":consequent:*:if_value")
                consequent_list = []
                if len(consequent_keys) > 0:
                    for key in consequent_keys:
                        k = key.split(":")
                        device_id = k[-2]
                        consequent = self.get_consequent(user_id, rule_id, device_id)
                        consequent_list.append(consequent)
                output = Rule(rule_id, rule_name, antecedent_list, consequent_list, rule_evaluation, last_true,
                              last_false, "")
            else:
                output = "error"
        except Exception as error:
            print(repr(error))
            return "error"
        else:
            return output

    def get_antecedent(self, user_id, rule_id, device_id):
        key_pattern = "user:" + user_id + ":rule:" + rule_id
        start_value = self.r.get(key_pattern + ":antecedent:" + device_id + ":start_value")
        stop_value = self.r.get(key_pattern + ":antecedent:" + device_id + ":stop_value")
        condition = self.r.get(key_pattern + ":antecedent:" + device_id + ":condition")
        evaluation = self.r.get(key_pattern + ":antecedent:" + device_id + ":evaluation")
        measure = self.r.get(key_pattern + ":antecedent:" + device_id + ":measure")
        device_name = self.r.get("device:" + device_id + ":name")
        value = "null"
        if "SWITCH" in device_id:
            if self.r.exists("device:" + device_id + ":measure"):
                value = self.r.get("device:" + device_id + ":last_on")
        else:
            if self.r.exists("device:" + device_id + ":absolute_measure"):
                absolute_measure = self.r.get("device:" + device_id + ":absolute_measure")
                value = self.device_antecedent_measure(device_id, absolute_measure)
        return Antecedent(device_id, device_name, start_value, stop_value, condition, evaluation, measure, value)

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

    def get_user_rules(self, user_id):
        try:
            rule_name_keys = self.r.scan("user:" + user_id + ":rule:*:name")
            output = []
            for key in rule_name_keys:
                rule_id = key.split(":")[-2]
                rule = self.get_user_rules_slim(user_id, rule_id)
                if rule != "error":
                    output.append(rule)
            output.sort(key=lambda r: datetime.strptime(r.registration_date, '%d/%m/%Y %H:%M:%S'))
        except Exception as error:
            print(repr(error))
            return "error"
        else:
            return output

    def get_user_rules_slim(self, user_id, rule_id):
        try:
            key_pattern = "user:" + user_id + ":rule:" + rule_id
            if self.r.exists(key_pattern + ":name") == 1:
                # get rule name
                rule_name = self.r.get(key_pattern + ":name")
                rule_evaluation = self.r.get(key_pattern + ":evaluation")
                registration_date = self.r.get(key_pattern + ":registration_date")
                output = Rule(rule_id, rule_name, [], [], rule_evaluation, "", "", registration_date)
            else:
                output = "error"
        except Exception as error:
            print(repr(error))
            return "error"
        else:
            return output
