from ruleapp.Rule.RuleFunctions import RuleFunction


class RuleServiceEvaluation(object):
    def __init__(self, redis):
        self.r = redis
        self.rule_functions = RuleFunction(redis)

    def rule_evaluation(self, user_id, rule_id):
        try:
            output = {"user_id": "", "rule_id": ""}
            trigger = self.rule_functions.rule_evaluation(user_id, rule_id)
            if trigger == "true":
                output["user_id"] = user_id
                output["rule_id"] = rule_id
            return output
        except Exception as error:
            print(repr(error))
            return output
