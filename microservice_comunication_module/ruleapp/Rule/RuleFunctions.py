from datetime import datetime


class RuleFunction(object):
    def __init__(self, redis):
        self.r = redis

    def rule_evaluation(self, user_id, rule_id):
        pattern_key = "user:" + user_id + ":rule:" + rule_id
        trigger = "false"
        if self.r.exists(pattern_key + ":name") == 1:
            old_evaluation = self.r.get(pattern_key + ":evaluation")
            antecedent_keys = self.r.scan(pattern_key + ":rule_antecedents:*:evaluation")
            new_evaluation = "false"
            consequents_status = self.check_consequents_status(user_id, rule_id)
            if consequents_status == "false":
                new_evaluation = "false"
            else:
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
        return new_evaluation

    def check_consequents_status(self, user_id, rule_id):
        key_pattern = "user:" + user_id + ":rule:" + rule_id
        device_consequents = self.r.lrange(key_pattern + ":device_consequents")
        consequents_status = "true"
        for device_id in device_consequents:
            if "alert" not in device_id and self.r.exists("device:" + device_id + ":measure") == 0:
                consequents_status = "false"
                break
        return consequents_status

    def update_evaluation_timestamp(self, pattern_key, evaluation):
        time_str = datetime.now().strftime("%H:%M")
        date_str = datetime.now().strftime("%d/%m/%Y")
        if evaluation == "true":
            self.r.set(pattern_key + ":last_time_on", time_str)
            self.r.set(pattern_key + ":last_date_on", date_str)
        else:
            self.r.set(pattern_key + ":last_time_off", time_str)
            self.r.set(pattern_key + ":last_date_off", date_str)
