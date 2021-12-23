from ruleapp.Devices.WaterLevel.WaterLevelAntecedentFunctions import WaterLevelAntecedentFunction
from ruleapp.Devices.Button.ButtonAntecedentFunctions import ButtonAntecedentFunction
from ruleapp.Devices.Photocell.PhotocellAntecedentFunctions import PhotocellAntecedentFunction
from ruleapp.Devices.DeviceId import WATER_LEVEL, BUTTON, PHOTOCELL


class AntecedentServiceEvaluation(object):
    def __init__(self, redis):
        self.r = redis
        self.waterlevel_antecedent_functions = WaterLevelAntecedentFunction(redis)
        self.button_antecedent_functions = ButtonAntecedentFunction(redis)
        self.photocell_antecedent_functions = PhotocellAntecedentFunction(redis)

    def antecedent_evaluation(self, user_id, device_id, measure, rules):
        output = []
        try:
            for rule_id in rules:
                trigger = "false"
                if WATER_LEVEL in device_id:
                    trigger = self.waterlevel_antecedent_functions.\
                        antecedent_evaluation(user_id, rule_id, device_id, measure)
                elif BUTTON in device_id:
                    trigger = self.button_antecedent_functions.\
                        antecedent_evaluation(user_id, rule_id, device_id, measure)
                elif PHOTOCELL in device_id:
                    trigger = self.photocell_antecedent_functions.\
                        antecedent_evaluation(user_id, rule_id, device_id, measure)
                if trigger == "true":
                    output.append(rule_id)
            return output
        except Exception as error:
            print(repr(error))
            return output
