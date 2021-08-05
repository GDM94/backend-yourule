from .RuleDTO import RuleDto
from ..Timer.TimerAntecedentFunctions import TimerAntecedentFunction
from ..Alert.AlertConsequentFunctions import AlertConsequentFunction


class RuleFunction(object):
    def __init__(self, redis):
        self.r = redis
        self.timer_antecedent_functions = TimerAntecedentFunction(redis)
        self.alert_consequent_functions = AlertConsequentFunction(redis)

    def get_rule(self, user_id, rule_id):
        try:
            key_pattern = "user:"+user_id+":rule:"+rule_id
            rule = RuleDto()
            rule.rule_id = rule_id
            rule.rule_name = self.r.get(key_pattern+":rule_name")
            rule.last_time_on = self.r.get(key_pattern+":last_time_on")
            rule.last_time_off = self.r.get(key_pattern+":last_time_off")
            rule.last_date_on = self.r.get(key_pattern+":last_date_on")
            rule.last_date_off = self.r.get(key_pattern+":last_date_off")
            rule.device_antecedents = self.r.lrange(key_pattern+":device_antecedents")
            rule.device_consequents = self.r.lrange(key_pattern+":device_consequents")
            rule.evaluation = self.r.get(key_pattern+":evaluation")
            rule.rule_antecedents = self.get_rule_antecedents(user_id, rule_id)
            rule.rule_consequents = self.get_rules_consequents(user_id, rule_id)
            return rule
        except Exception as error:
            print(repr(error))
            return "error"

    def get_rule_antecedents(self, user_id, rule_id):
        key_pattern = "user:"+user_id+":rule:"+rule_id
        device_antecedents = self.r.lrange(key_pattern+":device_antecedents")
        rule_antecedents = []
        for device_id in device_antecedents:
            rule_antecedents.append(self.get_antecedent(user_id, rule_id, device_id))
        return rule_antecedents

    def get_antecedent(self, user_id, rule_id, device_id):
        antecedent = {}
        if "timer" in device_id:
            antecedent = self.timer_antecedent_functions.get_antecedent_slim(user_id, rule_id, device_id)
        return antecedent

    def get_rules_consequents(self, user_id, rule_id):
        key_pattern = "user:"+user_id+":rule:"+rule_id
        device_consequents = self.r.lrange(key_pattern+":device_consequents")
        rule_consequents = []
        for device_id in device_consequents:
            rule_consequents.append(self.get_consequent(user_id, rule_id, device_id))
        return rule_consequents

    def get_consequent(self, user_id, rule_id, device_id):
        consequent = {}
        if "alert" in device_id:
            consequent = self.alert_consequent_functions.get_consequent_slim(user_id, rule_id, device_id)
        return consequent

    def get_rule_slim(self, user_id, rule_id):
        try:
            key_pattern = "user:"+user_id+":rule:"+rule_id
            rule = RuleDto()
            rule.rule_id = rule_id
            rule.rule_name = self.r.get(key_pattern+":rule_name")
            return rule
        except Exception as error:
            print(repr(error))
            return "error"

    def create_rule(self, user_id, rule_name):
        try:
            rule_id = str(self.r.incr("user:" + user_id + ":rule:counter"))
            key_pattern = "user:"+user_id+":rule:"+rule_id
            self.r.rpush("user:"+user_id+":rules", rule_id)
            self.r.set(key_pattern+":rule_name", rule_name)
            self.r.set(key_pattern+":evaluation", "false")
            rule = RuleDto()
            rule.rule_id = rule_id
            rule.rule_name = rule_name
            return rule
        except Exception as error:
            print(repr(error))
            return "error"

    def delete_rule(self, user_id, rule_id):
        key_pattern = "user:"+user_id+":rule:"+rule_id
        self.r.lrem("user:"+user_id+":rules", rule_id)
        self.r.delete(key_pattern+":rule_name")
        self.r.delete(key_pattern+":last_time_on")
        self.r.delete(key_pattern+":last_time_off")
        self.r.delete(key_pattern+":last_date_on")
        self.r.delete(key_pattern+":last_date_off")
        device_antecedents = self.r.lrange(key_pattern+":device_antecedents")
        for device_id in device_antecedents:
            self.delete_rule_antecedent(user_id, rule_id, device_id)
        device_consequents = self.r.lrange(key_pattern+":device_consequents")
        for device_id in device_consequents:
            self.delete_rule_consequent(user_id, rule_id, device_id)

    def delete_rule_antecedent(self, user_id, rule_id, device_id):
        key_pattern = "user:"+user_id+":rule:"+rule_id
        self.r.lrem(key_pattern+":device_antecedents", device_id)
        if "timer" in device_id:
            self.timer_antecedent_functions.delete_antecedent(user_id, rule_id, device_id)

    def delete_rule_consequent(self, user_id, rule_id, device_id):
        key_pattern = "user:"+user_id+":rule:"+rule_id
        self.r.lrem(key_pattern+":device_consequents", device_id)
        if "alert" in device_id:
            self.alert_consequent_functions.delete_consequent(user_id, rule_id, device_id)

    def update_rule_name(self, user_id, rule_id, rule_name):
        key_pattern = "user:"+user_id+":rule:"+rule_id
        self.r.set(key_pattern+":rule_name", rule_name)

    def add_rule_antecedent(self, user_id, rule_id, antecedent):
        key_pattern = "user:"+user_id+":rule:"+rule_id
        self.r.rpush(key_pattern+":device_antecedents", antecedent.device_id)
        self.update_rule_antecedent(user_id, rule_id, antecedent)

    def add_rule_consequent(self, user_id, rule_id, consequent):
        key_pattern = "user:"+user_id+":rule:"+rule_id
        self.r.rpush(key_pattern+":device_consequents", consequent.device_id)
        self.update_rule_consequent(user_id, rule_id, consequent)

    def update_rule_antecedent(self, user_id, rule_id, antecedent):
        if "timer" in antecedent.device_id:
            self.timer_antecedent_functions.set_antecedent(user_id, rule_id, antecedent)

    def update_rule_consequent(self, user_id, rule_id, consequent):
        if "alert" in consequent.device_id:
            self.alert_consequent_functions.set_consequent(user_id, rule_id, consequent)



