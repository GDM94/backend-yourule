from .RuleDTO import Rule
from ..Devices.Timer.TimerAntecedentFunctions import TimerAntecedentFunction
from ..Devices.Alert.AlertConsequentFunctions import AlertConsequentFunction
from ..Devices.WaterLevel.WaterLevelAntecedentFunctions import WaterLevelAntecedentFunction
from ..Devices.Switch.SwitchConsequentFunctions import SwitchConsequentFunction
from ..Devices.Button.ButtonAntecedentFunctions import ButtonAntecedentFunction
from datetime import datetime


class RuleFunction(object):
    def __init__(self, redis):
        self.r = redis
        self.timer_antecedent_functions = TimerAntecedentFunction(redis)
        self.alert_consequent_functions = AlertConsequentFunction(redis)
        self.waterlevel_antecedent_functions = WaterLevelAntecedentFunction(redis)
        self.switch_consequent_functions = SwitchConsequentFunction(redis)
        self.button_antecedent_functions = ButtonAntecedentFunction(redis)

    def create_rule(self, user_id, rule_name):
        try:
            rule_id = str(self.r.incr("user:" + user_id + ":rule:counter"))
            rule = Rule()
            rule.id = rule_id
            rule.name = rule_name
            key_pattern = "user:" + user_id + ":rule:" + rule_id
            self.r.rpush("user:" + user_id + ":rules", rule_id)
            self.r.set(key_pattern + ":name", rule_name)
            self.r.set(key_pattern + ":evaluation", "false")
            self.r.set(key_pattern + ":last_time_on", rule.last_time_on)
            self.r.set(key_pattern + ":last_time_off", rule.last_time_off)
            self.r.set(key_pattern + ":last_date_on", rule.last_date_on)
            self.r.set(key_pattern + ":last_date_off", rule.last_date_off)
            return rule
        except Exception as error:
            print(repr(error))
            return "error"

    def get_user_rules(self, user_id):
        try:
            rules_id_list = self.r.lrange("user:" + user_id + ":rules")
            output = []
            for rule_id in rules_id_list:
                key_pattern = "user:" + user_id + ":rule:" + rule_id
                if self.r.exists(key_pattern + ":name") == 1:
                    rule = Rule()
                    rule.name = self.r.get(key_pattern + ":name")
                    rule.id = rule_id
                    rule.evaluation = self.r.get(key_pattern + ":evaluation")
                    output.append(rule)
            return output
        except Exception as error:
            print(repr(error))
            return "error"

    def get_rule(self, user_id, rule_id):
        try:
            key_pattern = "user:" + user_id + ":rule:" + rule_id
            rule = Rule()
            rule.id = rule_id
            rule.name = self.r.get(key_pattern + ":name")
            rule.last_time_on = self.r.get(key_pattern + ":last_time_on")
            rule.last_time_off = self.r.get(key_pattern + ":last_time_off")
            rule.last_date_on = self.r.get(key_pattern + ":last_date_on")
            rule.last_date_off = self.r.get(key_pattern + ":last_date_off")
            rule.device_antecedents = self.r.lrange(key_pattern + ":device_antecedents")
            rule.device_consequents = self.r.lrange(key_pattern + ":device_consequents")
            rule.evaluation = self.r.get(key_pattern + ":evaluation")
            rule.rule_antecedents = self.get_rule_antecedents(user_id, rule_id)
            rule.rule_consequents = self.get_rule_consequents(user_id, rule_id)
            return rule
        except Exception as error:
            print(repr(error))
            return "error"

    def get_rule_antecedents(self, user_id, rule_id):
        try:
            key_pattern = "user:" + user_id + ":rule:" + rule_id
            device_antecedents = self.r.lrange(key_pattern + ":device_antecedents")
            rule_antecedents = []
            for device_id in device_antecedents:
                antecedent = self.get_rule_antecedent_slim(user_id, rule_id, device_id)
                if antecedent != "error":
                    rule_antecedents.append(antecedent)
                else:
                    raise Exception("error retrieving antecedent")
            return rule_antecedents
        except Exception as error:
            print(repr(error))
            return "error"

    def get_rule_antecedent(self, user_id, rule_id, device_id):
        try:
            antecedent = {}
            if "timer" in device_id:
                antecedent = self.timer_antecedent_functions.get_antecedent(user_id, rule_id, device_id)
            elif "WATERLEVEL" in device_id:
                antecedent = self.waterlevel_antecedent_functions.get_antecedent(user_id, rule_id, device_id)
            elif "BUTTON" in device_id:
                antecedent = self.button_antecedent_functions.get_antecedent(user_id, rule_id, device_id)
            return antecedent
        except Exception as error:
            print(repr(error))
            return "error"

    def get_rule_antecedent_slim(self, user_id, rule_id, device_id):
        try:
            antecedent = {}
            if "timer" in device_id:
                antecedent = self.timer_antecedent_functions.get_antecedent_slim(user_id, rule_id, device_id)
            elif "WATERLEVEL" in device_id:
                antecedent = self.waterlevel_antecedent_functions.get_antecedent_slim(user_id, rule_id, device_id)
            elif "BUTTON" in device_id:
                antecedent = self.button_antecedent_functions.get_antecedent_slim(user_id, rule_id, device_id)
            return antecedent
        except Exception as error:
            print(repr(error))
            return "error"

    def get_rule_consequents(self, user_id, rule_id):
        key_pattern = "user:" + user_id + ":rule:" + rule_id
        device_consequents = self.r.lrange(key_pattern + ":device_consequents")
        rule_consequents = []
        for device_id in device_consequents:
            consequent = self.get_rule_consequent_slim(user_id, rule_id, device_id)
            if consequent != "error":
                rule_consequents.append(consequent)
            else:
                raise Exception("error retrieving consequent")
        return rule_consequents

    def get_rule_consequent(self, user_id, rule_id, device_id):
        try:
            if "alert" in device_id:
                return self.alert_consequent_functions.get_consequent(user_id, rule_id, device_id)
            elif "SWITCH" in device_id:
                return self.switch_consequent_functions.get_consequent(user_id, rule_id, device_id)
        except Exception as error:
            print(repr(error))
            return "error"

    def get_rule_consequent_slim(self, user_id, rule_id, device_id):
        try:
            if "alert" in device_id:
                return self.alert_consequent_functions.get_consequent_slim(user_id, rule_id, device_id)
            elif "SWITCH" in device_id:
                return self.switch_consequent_functions.get_consequent_slim(user_id, rule_id, device_id)
        except Exception as error:
            print(repr(error))
            return "error"

    def delete_rule(self, user_id, rule_id):
        try:
            key_pattern = "user:" + user_id + ":rule:" + rule_id
            self.r.lrem("user:" + user_id + ":rules", rule_id)
            self.r.delete(key_pattern + ":name")
            self.r.delete(key_pattern + ":last_time_on")
            self.r.delete(key_pattern + ":last_time_off")
            self.r.delete(key_pattern + ":last_date_on")
            self.r.delete(key_pattern + ":last_date_off")
            device_antecedents = self.r.lrange(key_pattern + ":device_antecedents")
            for device_id in device_antecedents:
                self.delete_rule_antecedent(user_id, rule_id, device_id)
            device_consequents = self.r.lrange(key_pattern + ":device_consequents")
            for device_id in device_consequents:
                self.delete_rule_consequent(user_id, rule_id, device_id)
            return "true"
        except Exception as error:
            print(repr(error))
            return "error"

    def delete_rule_antecedent(self, user_id, rule_id, device_id):
        try:
            if "timer" in device_id:
                return self.timer_antecedent_functions.delete_antecedent(user_id, rule_id, device_id)
            elif "WATERLEVEL" in device_id:
                return self.waterlevel_antecedent_functions.delete_antecedent(user_id, rule_id, device_id)
            elif "BUTTON" in device_id:
                return self.button_antecedent_functions.delete_antecedent(user_id, rule_id, device_id)
        except Exception as error:
            print(repr(error))
            return "error"

    def delete_rule_consequent(self, user_id, rule_id, device_id):
        try:
            if "alert" in device_id:
                return self.alert_consequent_functions.delete_consequent(user_id, rule_id, device_id)
            elif "SWITCH" in device_id:
                return self.switch_consequent_functions.delete_consequent(user_id, rule_id, device_id)
        except Exception as error:
            print(repr(error))
            return "error"

    def update_rule_name(self, user_id, rule_id, rule_name):
        try:
            key_pattern = "user:" + user_id + ":rule:" + rule_id
            self.r.set(key_pattern + ":name", rule_name)
            return "true"
        except Exception as error:
            print(repr(error))
            return "error"

    def add_rule_antecedent(self, user_id, rule_id, device_id):
        try:
            if "timer" in device_id:
                return self.timer_antecedent_functions.add_antecedent(user_id, rule_id, device_id)
            elif "WATERLEVEL" in device_id:
                return self.waterlevel_antecedent_functions.add_antecedent(user_id, rule_id, device_id)
            elif "BUTTON" in device_id:
                return self.button_antecedent_functions.add_antecedent(user_id, rule_id, device_id)
        except Exception as error:
            print(repr(error))
            return "error"

    def add_rule_consequent(self, user_id, rule_id, device_id):
        try:
            if "alert" in device_id:
                return self.alert_consequent_functions.add_consequent(user_id, rule_id, device_id)
            elif "SWITCH" in device_id:
                return self.switch_consequent_functions.add_consequent(user_id, rule_id, device_id)
        except Exception as error:
            print(repr(error))
            return "error"

    def update_rule_antecedent(self, user_id, rule_id, device_id, antecedent_json):
        try:
            antecedent = {}
            if "timer" in device_id:
                antecedent = self.timer_antecedent_functions.update_antecedent(user_id, rule_id, antecedent_json)
            elif "WATERLEVEL" in device_id:
                antecedent = self.waterlevel_antecedent_functions.update_antecedent(user_id, rule_id, antecedent_json)
            elif "BUTTON" in device_id:
                antecedent = self.button_antecedent_functions.update_antecedent(user_id, rule_id, antecedent_json)
            return antecedent
        except Exception as error:
            print(repr(error))
            return "error"

    def update_rule_consequent(self, user_id, rule_id, device_id, consequent_json):
        try:
            result = "true"
            if "alert" in device_id:
                result = self.alert_consequent_functions.update_consequent(user_id, rule_id, consequent_json)
            elif "SWITCH" in device_id:
                result = self.switch_consequent_functions.update_consequent(user_id, rule_id, consequent_json)
            return result
        except Exception as error:
            print(repr(error))
            return "error"

    def update_rule_consequents_order(self, user_id, rule_id, consequents_id_list):
        try:
            self.r.delete("user:" + user_id + ":rule:" + rule_id + ":device_consequents")
            order = 0
            for device_id in consequents_id_list:
                self.r.rpush("user:" + user_id + ":rule:" + rule_id + ":device_consequents", device_id)
                key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_consequents:" + device_id
                self.r.set(key_pattern + ":delay", "0")
                self.r.set(key_pattern + ":order", str(order))
                order = order + 1
            return "true"
        except Exception as error:
            print(repr(error))
            return "error"

    def rule_evaluation(self, user_id, rule_id):
        pattern_key = "user:" + user_id + ":rule:" + rule_id
        trigger = "false"
        if self.r.exists(pattern_key + ":name") == 1:
            old_evaluation = self.r.get(pattern_key + ":evaluation")
            antecedent_keys = self.r.scan(pattern_key + ":rule_antecedents:*:evaluation")
            new_evaluation = "false"
            if len(antecedent_keys) > 0:
                new_evaluation = self.check_antecedent_evaluation(antecedent_keys)
            if old_evaluation != new_evaluation:
                self.r.set(pattern_key + ":evaluation", new_evaluation)
                self.update_evaluation_timestamp(pattern_key, new_evaluation)
                trigger = "true"
        return trigger

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
                if "timer" not in antecedent_device_id and self.r.exists(
                        "device:" + antecedent_device_id + ":measure") == 0:
                    new_evaluation = "false"
                    break
        return new_evaluation

    def update_evaluation_timestamp(self, pattern_key, evaluation):
        time_str = datetime.now().strftime("%%H:%M:%S")
        date_str = datetime.now().strftime("%d/%m/%Y")
        if evaluation == "true":
            self.r.set(pattern_key + ":last_time_on", time_str)
            self.r.set(pattern_key + ":last_date_on", date_str)
        else:
            self.r.set(pattern_key + ":last_time_off", time_str)
            self.r.set(pattern_key + ":last_date_off", date_str)
