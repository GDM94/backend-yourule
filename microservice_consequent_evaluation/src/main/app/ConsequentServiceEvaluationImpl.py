import json
from ruleapp.Devices.Alert.AlertConsequentFunctions import AlertConsequentFunction
from ruleapp.Devices.Switch.SwitchConsequentFunctions import SwitchConsequentFunction


class ConsequentServiceEvaluation(object):
    def __init__(self, config, redis):
        self.r = redis
        self.email_user = config.get("ALERT", "email_user")
        self.email_password = config.get("ALERT", "email_password")
        self.alert_consequent_functions = AlertConsequentFunction(config, redis)
        self.switch_consequent_functions = SwitchConsequentFunction(redis)

    def consequent_order_delay(self, user_id, rule_id, consequent_keys):
        pattern_key = "user:" + user_id + ":rule:" + rule_id
        consequent_list_unordered = []
        for key in consequent_keys:
            consequent_obj = {}
            device_id = key.split(":")[-2]
            order = self.r.get(pattern_key + ":consequent:" + device_id + ":order")
            delay = self.r.get(pattern_key + ":consequent:" + device_id + ":delay")
            consequent_obj["device_id"] = device_id
            consequent_obj["order"] = int(order)
            consequent_obj["delay"] = int(delay)
            consequent_list_unordered.append(consequent_obj)
        consequent_list_ordered = sorted(consequent_list_unordered, key=lambda k: k['order'])
        delay = 0
        consequent_list_ordered_delay = []
        for consequent in consequent_list_ordered:
            delay = delay + consequent["delay"]
            consequent["delay"] = delay
            consequent_list_ordered_delay.append(consequent)
        return consequent_list_ordered_delay

    def consequent_evaluation(self, payload):
        output = {"device_id": [], "measure": [], "delay": []}
        try:
            trigger = json.loads(payload)
            user_id = str(trigger["user_id"])
            rule_id = str(trigger["rule_id"])
            pattern_key = "user:" + user_id + ":rule:" + rule_id
            consequent_keys = self.r.scan(pattern_key + ":consequent:*:order")
            consequent_list_ordered_delay = self.consequent_order_delay(user_id, rule_id, consequent_keys)
            for consequent in consequent_list_ordered_delay:
                device_id = consequent["device_id"]
                delay = str(consequent["delay"])
                if "alert" not in device_id:
                    switch_measure = self.switch_consequent_functions.switch_evaluation(user_id, device_id)
                    if switch_measure != "false":
                        output["device_id"].append(device_id)
                        output["measure"].append(switch_measure)
                        output["delay"].append(delay)
                else:
                    self.alert_consequent_functions.alert_evaluation(user_id, rule_id)
            return output
        except Exception as error:
            print(repr(error))
            return output
