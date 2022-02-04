from ruleapp.Devices.WaterLevel.WaterLevelAntecedentFunctions import WaterLevelAntecedentFunction
from ruleapp.Devices.Button.ButtonAntecedentFunctions import ButtonAntecedentFunction
from ruleapp.Devices.Photocell.PhotocellAntecedentFunctions import PhotocellAntecedentFunction
from ruleapp.Rule.RuleFunctions import RuleFunction
from ruleapp.Devices.Alert.AlertConsequentFunctions import AlertConsequentFunction
from ruleapp.Devices.Switch.SwitchConsequentFunctions import SwitchConsequentFunction
from ruleapp.Devices.Servo.ServoConsequentFunctions import ServoConsequentFunction
from ruleapp.Devices.DeviceId import WATER_LEVEL, BUTTON, PHOTOCELL, SWITCH, ALERT, SERVO


class FunctionalRuleService(object):
    def __init__(self, redis, config):
        self.r = redis
        self.waterlevel_antecedent_functions = WaterLevelAntecedentFunction(redis)
        self.button_antecedent_functions = ButtonAntecedentFunction(redis)
        self.photocell_antecedent_functions = PhotocellAntecedentFunction(redis)
        self.rule_functions = RuleFunction(redis)
        self.email_user = config.get("ALERT", "email_user")
        self.email_password = config.get("ALERT", "email_password")
        self.alert_consequent_functions = AlertConsequentFunction(redis)
        self.switch_consequent_functions = SwitchConsequentFunction(redis)
        self.servo_consequent_functions = ServoConsequentFunction(redis)

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

    def consequent_evaluation(self, user_id, rule_id):
        output = []
        pattern_key = "user:" + user_id + ":rule:" + rule_id
        device_consequents = self.r.lrange(pattern_key + ":device_consequents")
        alert_id = next((s for s in device_consequents if ALERT in s), "")
        if alert_id != "":
            self.alert_consequent_functions.alert_evaluation(user_id, rule_id)
        delay = 0
        for device_id in device_consequents:
            delay = delay + int(self.r.get(pattern_key + ":rule_consequents:" + device_id + ":delay"))
            measure = "false"
            if SWITCH in device_id:
                measure = self.switch_consequent_functions.switch_evaluation(user_id, device_id)
            elif SERVO in device_id:
                measure = self.servo_consequent_functions.servo_evaluation(user_id, device_id)
            if measure != "false":
                trigger = {"device_id": device_id, "measure": measure, "delay": str(delay)}
                output.append(trigger)
        payload = {"output": output}
        return payload
