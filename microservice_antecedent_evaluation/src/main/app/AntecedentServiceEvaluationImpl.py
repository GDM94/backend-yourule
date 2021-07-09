from .dto.AntecedentEvaluationDTO import AntecedentEvaluation


class AntecedentServiceEvaluation(object):
    def __init__(self, redis):
        self.r = redis

    def antecedent_evaluation(self, trigger):
        output = AntecedentEvaluation(trigger["user_id"], [])
        try:
            for rule_id in trigger["rules"]:
                if self.r.exists("user:" + trigger["user_id"] + ":rule:" + rule_id + ":name") == 1:
                    key_pattern = "user:" + trigger["user_id"] + ":rule:" + rule_id + ":antecedent:" + trigger[
                        "device_id"]
                    evaluation = "false"
                    old_evaluation = self.r.get(key_pattern + ":evaluation")
                    condition = self.r.get(key_pattern + ":condition")
                    start_value = self.r.get(key_pattern + ":start_value")
                    measure = trigger["measure"]
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
                    elif condition == "=":
                        if measure == start_value:
                            evaluation = "true"
                    elif condition == "isteresi":
                        stop_value = self.r.get(key_pattern + ":stop_value")
                        if int(measure) <= int(start_value):
                            evaluation = "true"
                        if old_evaluation == "true" and int(measure) <= int(stop_value):
                            evaluation = "true"
                    if evaluation != old_evaluation:
                        self.r.set(key_pattern + ":evaluation", evaluation)
                        output.rules.append(rule_id)
        except Exception as error:
            print(repr(error))
            return output
        else:
            return output
