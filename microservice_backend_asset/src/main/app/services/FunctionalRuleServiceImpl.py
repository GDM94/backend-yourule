from ruleapp.Devices.WaterLevel.WaterLevelAntecedentFunctions import WaterLevelAntecedentFunction
from ruleapp.Devices.Button.ButtonAntecedentFunctions import ButtonAntecedentFunction
from ruleapp.Devices.Photocell.PhotocellAntecedentFunctions import PhotocellAntecedentFunction
from ruleapp.Rule.RuleFunctions import RuleFunction
from ruleapp.Devices.DeviceId import WATER_LEVEL, BUTTON, PHOTOCELL


class FunctionalRuleService(object):
    def __init__(self, redis, config):
        self.waterlevel_antecedent_functions = WaterLevelAntecedentFunction(redis)
        self.button_antecedent_functions = ButtonAntecedentFunction(redis)
        self.photocell_antecedent_functions = PhotocellAntecedentFunction(redis)
        self.rule_functions = RuleFunction(redis)

    def antecedent_evaluation(self, user_id, device_id, measure, rules):
        output = []
        for rule_id in rules:
            trigger = "false"
            if WATER_LEVEL in device_id:
                trigger = self.waterlevel_antecedent_functions. \
                    antecedent_evaluation(user_id, rule_id, device_id, measure)
            elif BUTTON in device_id:
                trigger = self.button_antecedent_functions. \
                    antecedent_evaluation(user_id, rule_id, device_id, measure)
            elif PHOTOCELL in device_id:
                trigger = self.photocell_antecedent_functions. \
                    antecedent_evaluation(user_id, rule_id, device_id, measure)
            if trigger == "true":
                output.append(rule_id)
        trigger = {"rules": output, "user_id": str(user_id)}
        return trigger

    def rule_evaluation(self, user_id, rules):
        rule_list = []
        for rule_id in rules:
            output = self.rule_functions.rule_evaluation(user_id, rule_id)
            if output == "true":
                rule_list.append(rule_id)
        trigger = {"user_id": user_id, "rules": rule_list}
        return trigger
