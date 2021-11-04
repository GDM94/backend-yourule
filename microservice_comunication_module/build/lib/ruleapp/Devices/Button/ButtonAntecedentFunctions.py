from .ButtonAntecedentDTO import ButtonAntecedent


class ButtonAntecedentFunction(object):
    def __init__(self, redis):
        self.r = redis

    def get_antecedent(self, user_id, rule_id, device_id):
        try:
            antecedent = ButtonAntecedent()
            key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_antecedents:" + device_id
            device_key_pattern = "device:" + device_id
            antecedent.device_id = device_id
            antecedent.device_name = self.r.get(device_key_pattern + ":name")
            if self.r.exists(device_key_pattern + ":measure"):
                antecedent.measure = self.r.get(device_key_pattern + ":measure")
            antecedent.evaluation = self.r.get(key_pattern + ":evaluation")
            antecedent.last_time_on = self.r.get(key_pattern + ":last_time_on")
            antecedent.last_time_off = self.r.get(key_pattern + ":last_time_off")
            antecedent.last_date_on = self.r.get(key_pattern + ":last_date_on")
            antecedent.last_date_off = self.r.get(key_pattern + ":last_date_off")
            return antecedent
        except Exception as error:
            print(repr(error))
            return "error"

    def get_antecedent_slim(self, user_id, rule_id, device_id):
        try:
            antecedent = ButtonAntecedent()
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
            self.r.lrem("device:" + device_id + ":rules", rule_id)
            self.r.lrem("user:" + user_id + ":rule:" + rule_id + ":device_antecedents", device_id)
            key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_antecedents:" + device_id
            self.r.delete(key_pattern + ":measure")
            self.r.delete(key_pattern + ":evaluation")
            self.r.delete(key_pattern + ":last_time_on")
            self.r.delete(key_pattern + ":last_time_off")
            self.r.delete(key_pattern + ":last_date_on")
            self.r.delete(key_pattern + ":last_date_off")
            return "true"
        except Exception as error:
            print(repr(error))
            return "error"

    def add_antecedent(self, user_id, rule_id, device_id):
        try:
            device_antecedents = self.r.lrange("user:" + user_id + ":rule:" + rule_id + ":device_antecedents")
            result = "false"
            if device_id not in device_antecedents:
                self.r.rpush("device:" + device_id + ":rules", rule_id)
                self.r.rpush("user:" + user_id + ":rule:" + rule_id + ":device_antecedents", device_id)
                result = "true"
            return result
        except Exception as error:
            print(repr(error))
            return "error"

    def update_antecedent(self, user_id, rule_id, new_antecedent):
        try:
            antecedent = ButtonAntecedent()
            antecedent.antecedent_mapping(new_antecedent)
            device_antecedents = self.r.lrange("user:" + user_id + ":rule:" + rule_id + ":device_antecedents")
            result = "false"
            if antecedent.device_id in device_antecedents:
                result = "true"
            return result
        except Exception as error:
            print(repr(error))
            return "error"

    def antecedent_evaluation(self, user_id, rule_id, device_id, measure):
        try:
            evaluation = "false"
            if self.r.exists("device:" + device_id + ":measure") == 1:
                evaluation = self.evaluate_measure(measure)
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

    def evaluate_measure(self, measure):
        try:
            evaluation = "false"
            if measure == "on":
                evaluation = "true"
            return evaluation
        except Exception as error:
            print(repr(error))
            return "error"
