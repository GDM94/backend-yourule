from ruleapp.Devices.WaterLevel.WaterLevelAntecedentFunctions import WaterLevelAntecedentFunction
from ruleapp.Devices.Button.ButtonAntecedentFunctions import ButtonAntecedentFunction


class AntecedentServiceEvaluation(object):
    def __init__(self, redis):
        self.r = redis
        self.waterlevel_antecedent_functions = WaterLevelAntecedentFunction(redis)
        self.button_antecedent_functions = ButtonAntecedentFunction(redis)

    def antecedent_evaluation(self, user_id, device_id, measure, rules):
        output = []
        try:
            for rule_id in rules:
                trigger = "false"
                if "WATERLEVEL" in device_id:
                    trigger = self.waterlevel_antecedent_functions.\
                        antecedent_evaluation(user_id, rule_id, device_id, measure)
                elif "BUTTON" in device_id:
                    trigger = self.button_antecedent_functions.\
                        antecedent_evaluation(user_id, rule_id, device_id, measure)
                if trigger == "true":
                    output.append(rule_id)
            return output
        except Exception as error:
            print(repr(error))
            return output
