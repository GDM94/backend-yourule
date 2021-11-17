from .SwitchAntecedentDTO import SwitchAntecedent
from datetime import datetime


class SwitchAntecedentFunction(object):
    def __init__(self, redis):
        self.r = redis

    def get_antecedent(self, user_id, rule_id, device_id):
        try:
            antecedent = SwitchAntecedent()
            rule_key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_antecedents:" + device_id
            device_key_pattern = "device:" + device_id
            antecedent.device_id = device_id
            antecedent.device_name = self.r.get(device_key_pattern + ":name")
            antecedent.last_time_on = self.r.get(device_key_pattern + ":last_time_on")
            antecedent.last_date_on = self.r.get(device_key_pattern + ":last_date_on")
            antecedent.last_time_off = self.r.get(device_key_pattern + ":last_time_off")
            antecedent.last_date_off = self.r.get(device_key_pattern + ":last_date_off")
            if self.r.exists(device_key_pattern + ":measure"):
                antecedent.measure = self.r.get(device_key_pattern + ":measure")
            antecedent.evaluation = self.r.get(rule_key_pattern + ":evaluation")
            antecedent.time_start_value = self.r.get(rule_key_pattern + ":time_start_value")
            antecedent.time_stop_value = self.r.get(rule_key_pattern + ":time_stop_value")
            antecedent.date_start_value = self.r.get(rule_key_pattern + ":date_start_value")
            antecedent.date_stop_value = self.r.get(rule_key_pattern + ":date_stop_value")
            return antecedent
        except Exception as error:
            print(repr(error))
            return "error"

    def get_antecedent_slim(self, user_id, rule_id, device_id):
        try:
            antecedent = SwitchAntecedent()
            key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_antecedents:" + device_id
            antecedent.device_id = device_id
            antecedent.device_name = self.r.get("device:" + device_id + ":name")
            antecedent.evaluation = self.r.get(key_pattern + ":evaluation")
            return antecedent
        except Exception as error:
            print(repr(error))
            return "error"

    def delete_antecedent(self, user_id, rule_id, device_id):
        try:
            self.r.lrem("user:" + user_id + ":rule:" + rule_id + ":device_antecedents", device_id)
            key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_antecedents:" + device_id
            self.r.delete(key_pattern + ":evaluation")
            self.r.delete(key_pattern + ":last_time_on")
            self.r.delete(key_pattern + ":last_time_off")
            self.r.delete(key_pattern + ":last_date_on")
            self.r.delete(key_pattern + ":last_date_off")
            self.r.delete(key_pattern + ":time_start_value")
            self.r.delete(key_pattern + ":time_stop_value")
            self.r.delete(key_pattern + ":date_start_value")
            self.r.delete(key_pattern + ":date_stop_value")
            return "true"
        except Exception as error:
            print(repr(error))
            return "error"

    def add_antecedent(self, user_id, rule_id, device_id):
        try:
            device_antecedents = self.r.lrange("user:" + user_id + ":rule:" + rule_id + ":device_antecedents")
            device_consequents = self.r.lrange("user:" + user_id + ":rule:" + rule_id + ":device_consequents")
            result = "false"
            if device_id not in device_antecedents and device_id in device_consequents:
                self.r.rpush("user:" + user_id + ":rule:" + rule_id + ":device_antecedents", device_id)
                key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_antecedents:" + device_id
                antecedent = SwitchAntecedent()
                self.r.set(key_pattern + ":evaluation", antecedent.evaluation)
                self.r.set(key_pattern + ":time_start_value", antecedent.time_start_value)
                self.r.set(key_pattern + ":time_stop_value", antecedent.time_stop_value)
                self.r.set(key_pattern + ":date_start_value", antecedent.date_start_value)
                self.r.set(key_pattern + ":date_stop_value", antecedent.date_stop_value)
                result = "true"
            return result
        except Exception as error:
            print(repr(error))
            return "error"

    def update_antecedent(self, user_id, rule_id, new_antecedent):
        try:
            antecedent = SwitchAntecedent()
            antecedent.antecedent_mapping(new_antecedent)
            device_antecedents = self.r.lrange("user:" + user_id + ":rule:" + rule_id + ":device_antecedents")
            result = "false"
            if antecedent.device_id in device_antecedents:
                key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_antecedents:" + antecedent.device_id
                self.r.set(key_pattern + ":time_start_value", antecedent.time_start_value)
                self.r.set(key_pattern + ":time_stop_value", antecedent.time_stop_value)
                self.r.set(key_pattern + ":date_start_value", antecedent.date_start_value)
                self.r.set(key_pattern + ":date_stop_value", antecedent.date_stop_value)
                result = "true"
            return result
        except Exception as error:
            print(repr(error))
            return "error"

    def antecedent_evaluation(self, user_id, device_id, rule_id):
        try:
            evaluation = self.last_time_evaluation(user_id, device_id, rule_id)
            key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_antecedents:" + device_id
            old_evaluation = self.r.get(key_pattern + ":evaluation")
            trigger = "false"
            if evaluation != old_evaluation:
                self.r.set(key_pattern + ":evaluation", evaluation)
                trigger = "true"
            return trigger
        except Exception as error:
            print(repr(error))
            return "error"

    def last_time_evaluation(self, user_id, device_id, rule_id):
        key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_antecedents:" + device_id
        device_key_pattern = "device:" + device_id
        evaluation = "false"
        if self.r.exists(device_key_pattern + ":measure") == 1:
            measure = self.r.get(device_key_pattern + ":measure")
            last_time_on_str = self.r.get(device_key_pattern + ":last_time_on")
            last_time_off_str = self.r.get(device_key_pattern + ":last_time_off")
            time_stop_value_str = self.r.get(key_pattern + ":time_stop_value")
            time_start_value_str = self.r.get(key_pattern + ":time_start_value")
            if last_time_on_str == "" or last_time_off_str == "" or time_stop_value_str == "-" or time_start_value_str == "-":
                return "true"
            last_time_on = datetime.strptime(last_time_on_str, '%H:%M')
            last_time_off = datetime.strptime(last_time_off_str, '%H:%M')
            if measure == "on":
                delta_last_off = (last_time_on - last_time_off).total_seconds()
                time_stop_value = datetime.strptime(time_stop_value_str, '%H:%M').time()
                date_stop_value = int(self.r.get(key_pattern + ":date_stop_value")) * 24 * 60
                stop_interval = (time_stop_value.hour * 60) + time_stop_value.minute + date_stop_value
                evaluation = "true"
                if stop_interval < delta_last_off:
                    evaluation = "false"
            elif measure == "off":
                delta_last_on = (last_time_off - last_time_on).total_seconds()
                time_start_value = datetime.strptime(time_start_value_str, '%H:%M').time()
                date_start_value = int(self.r.get(key_pattern + ":date_start_value")) * 24 * 60
                start_inteval = (time_start_value.hour * 60) + time_start_value.minute + date_start_value
                evaluation = "false"
                if start_inteval < delta_last_on:
                    evaluation = "true"
        return evaluation
