from ruleapp.Devices.Alert.AlertConsequentFunctions import AlertConsequentFunction
from ruleapp.Devices.Switch.SwitchConsequentFunctions import SwitchConsequentFunction


class ConsequentServiceEvaluation(object):
    def __init__(self, config, redis):
        self.r = redis
        self.email_user = config.get("ALERT", "email_user")
        self.email_password = config.get("ALERT", "email_password")
        self.alert_consequent_functions = AlertConsequentFunction(redis)
        self.switch_consequent_functions = SwitchConsequentFunction(redis)

    def switch_evaluation(self, user_id, rule_id):
        output = []
        try:
            pattern_key = "user:" + user_id + ":rule:" + rule_id
            device_consequents = self.r.lrange(pattern_key + ":device_consequents")
            delay = 0
            for device_id in device_consequents:
                delay = delay + int(self.r.get(pattern_key + ":rule_consequents:" + device_id + ":delay"))
                if "alert" not in device_id:
                    measure = self.switch_consequent_functions.switch_evaluation(user_id, device_id)
                    if measure != "false":
                        trigger = {"device_id": device_id, "measure": measure, "delay": str(delay)}
                        output.append(trigger)
            return output
        except Exception as error:
            print(repr(error))
            return output

    def alert_evaluation(self, user_id, rule_id):
        try:
            pattern_key = "user:" + user_id + ":rule:" + rule_id
            device_consequents = self.r.lrange(pattern_key + ":device_consequents")
            for device_id in device_consequents:
                if "alert" in device_id:
                    self.alert_consequent_functions.alert_evaluation(user_id, rule_id)
                    break
        except Exception as error:
            print(repr(error))
