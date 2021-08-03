import json


class SwitchServiceEvaluation(object):
    def __init__(self, redis):
        self.r = redis

    def switch_evaluation(self, payload):
        output = {"device_id": "", "measure": ""}
        try:
            trigger = json.loads(payload)
            user_id = str(trigger["user_id"])
            device_id = str(trigger["device_id"])
            measure = str(trigger["measure"])
            key_pattern = "device:" + device_id
            automatic = self.r.get(key_pattern + ":automatic")
            if automatic == "true":
                rules = list(self.r.smembers(key_pattern + ":rules"))
                status = "off"
                for rule in rules:
                    if self.r.get("user:" + user_id + ":rule:" + rule + ":evaluation") == "true":
                        status = "on"
                        break
            else:
                status = self.r.get(key_pattern+":manual_measure")
            if measure != status:
                output["device_id"] = device_id
                output["measure"] = status
        except Exception as error:
            print(repr(error))
            return output
        else:
            return output
