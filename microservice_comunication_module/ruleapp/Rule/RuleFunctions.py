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
