from .WaterLevelAntecedentDTO import WaterLevelAntecedent
from datetime import datetime


class WaterLevelAntecedentFunction(object):
    def __init__(self, redis):
        self.r = redis

    def get_antecedent(self, user_id, rule_id, device_id):
        try:
            antecedent = WaterLevelAntecedent()
            key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_antecedents:" + device_id
            antecedent.device_id = device_id
            antecedent.device_name = self.r.get(key_pattern + ":device_name")
            antecedent.measure = self.r.get(key_pattern + ":measure")
            antecedent.absolute_measure = self.r.get(key_pattern + ":absolute_measure")
            antecedent.condition_measure = self.r.get(key_pattern + ":condition_measure")
            antecedent.start_value = self.r.get(key_pattern + ":start_value")
            antecedent.stop_value = self.r.get(key_pattern + ":stop_value")
            antecedent.evaluation = self.r.get(key_pattern + ":evaluation")
            antecedent.last_time_on = self.r.get(key_pattern + ":last_time_on")
            antecedent.last_time_off = self.r.get(key_pattern + ":last_time_off")
            antecedent.last_date_on = self.r.get(key_pattern + ":last_date_on")
            antecedent.last_date_off = self.r.get(key_pattern + ":last_date_off")
            antecedent.order = self.r.get(key_pattern + ":order")
            return antecedent
        except Exception as error:
            print(repr(error))
            return "error"

    def get_antecedent_slim(self, user_id, rule_id, device_id):
        try:
            antecedent = WaterLevelAntecedent()
            key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_antecedents:" + device_id
            antecedent.device_id = device_id
            antecedent.device_name = self.r.get(key_pattern + ":device_name")
            antecedent.evaluation = self.r.get(key_pattern + ":evaluation")
            antecedent.order = self.r.get(key_pattern + ":order")
            return antecedent
        except Exception as error:
            print(repr(error))
            return "error"

    def delete_antecedent(self, user_id, rule_id, device_id):
        try:
            self.r.lrem("device:" + device_id + ":rules", rule_id)
            self.r.lrem("user:" + user_id + ":rule:" + rule_id + ":device_antecedents", device_id)
            key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_antecedents:" + device_id
            self.r.delete(key_pattern + ":device_name")
            self.r.delete(key_pattern + ":measure")
            self.r.delete(key_pattern + ":condition_measure")
            self.r.delete(key_pattern + ":start_value")
            self.r.delete(key_pattern + ":stop_value")
            self.r.delete(key_pattern + ":evaluation")
            self.r.delete(key_pattern + ":last_time_on")
            self.r.delete(key_pattern + ":last_time_off")
            self.r.delete(key_pattern + ":last_date_on")
            self.r.delete(key_pattern + ":last_date_off")
            self.r.delete(key_pattern + ":order")
            return "true"
        except Exception as error:
            print(repr(error))
            return "error"

    def set_antecedent(self, user_id, rule_id, antecedent_json):
        try:
            antecedent = WaterLevelAntecedent()
            antecedent.json_mapping(antecedent_json)
            self.r.rpush("device:" + antecedent.device_id + ":rules", rule_id)
            self.r.rpush("user:" + user_id + ":rule:" + rule_id + ":device_antecedents", antecedent.device_id)
            key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_antecedents:" + antecedent.device_id
            self.r.set(key_pattern + ":device_name", antecedent.device_name)
            self.r.set(key_pattern + ":condition_measure", antecedent.condition_measure)
            self.r.set(key_pattern + ":start_value", antecedent.start_value)
            self.r.set(key_pattern + ":stop_value", antecedent.stop_value)
            self.r.set(key_pattern + ":order", antecedent.order)
            return "true"
        except Exception as error:
            print(repr(error))
            return "error"

    def device_antecedent_measure(self, device_id, absolute_measure):
        key_pattern = "device:" + device_id
        max_measure = int(self.r.get(key_pattern + ":setting:max"))
        error_setting = int(self.r.get(key_pattern + ":setting:error"))
        relative_measure = float(absolute_measure) - float(error_setting)
        measure = str(round((1 - (relative_measure / float(max_measure))) * 100.0))
        self.r.set(key_pattern + ":measure", measure)
        self.r.set(key_pattern + ":absolute_measure", str(absolute_measure))
        return measure

    def evaluate_antecedent(self, user_id, rule_id, device_id, measure):
        try:
            time_evaluation = self.evaluate_measure(user_id, rule_id, device_id, measure)
            evaluation = "false"
            if time_evaluation == "true":
                evaluation = "true"
            return evaluation
        except Exception as error:
            print(repr(error))
            return "error"

    def evaluate_measure(self, user_id, rule_id, device_id, measure):
        try:
            key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_antecedents:" + device_id
            evaluation = "false"
            old_evaluation = self.r.get(key_pattern + ":evaluation")
            condition = self.r.get(key_pattern + ":condition_measure")
            start_value = self.r.get(key_pattern + ":start_value")
            if condition == "between":
                stop_value = self.r.get(key_pattern + ":stop_value")
                if int(start_value) <= int(measure) < int(stop_value):
                    evaluation = "true"
            elif condition == ">":
                if int(measure) > int(start_value):
                    evaluation = "true"
            elif condition == "<":
                if int(measure) < int(start_value):
                    evaluation = "true"
            elif condition == "isteresi":
                stop_value = self.r.get(key_pattern + ":stop_value")
                if int(measure) <= int(start_value):
                    evaluation = "true"
                if old_evaluation == "true" and int(measure) <= int(stop_value):
                    evaluation = "true"
            return evaluation
        except Exception as error:
            print(repr(error))
            return "error"

