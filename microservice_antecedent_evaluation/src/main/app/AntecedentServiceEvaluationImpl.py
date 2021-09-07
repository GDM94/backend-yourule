from .dto.AntecedentEvaluationDTO import AntecedentEvaluation
from .dto.devices.WaterLevel.WaterLevelAntecedentFunctions import WaterLevelAntecedentFunction
from .dto.devices.Button.ButtonAntecedentFunctions import ButtonAntecedentFunction


class AntecedentServiceEvaluation(object):
    def __init__(self, redis):
        self.r = redis
        self.waterlevel_functions = WaterLevelAntecedentFunction(redis)
        self.button_functions = ButtonAntecedentFunction(redis)

    def antecedent_evaluation(self, user_id, device_id, measure, rules):
        output = AntecedentEvaluation(user_id, [])
        try:
            for rule_id in rules:
                trigger = "false"
                if "WATERLEVEL" in device_id:
                    trigger = self.waterlevel_functions.antecedent_evaluation(user_id, rule_id, device_id, measure)
                elif "BUTTON" in device_id:
                    trigger = self.button_functions.antecedent_evaluation(user_id, rule_id, device_id, measure)
                if trigger == "true":
                    output.rules.append(rule_id)
            return output
        except Exception as error:
            print(repr(error))
            return output
