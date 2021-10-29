from .SwitchConsequentDTO import SwitchConsequent


class SwitchConsequentFunction(object):
    def __init__(self, redis):
        self.r = redis

    def get_consequent(self, user_id, rule_id, device_id):
        try:
            dto = SwitchConsequent()
            key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_consequents:" + device_id
            dto.device_id = device_id
            dto.device_name = self.r.get("device:" + device_id + ":name")
            dto.delay = self.r.get(key_pattern + ":delay")
            dto.order = self.r.get(key_pattern + ":order")
            dto.automatic = self.r.get("device:" + device_id + ":automatic")
            return dto
        except Exception as error:
            print(repr(error))
            return "error"

    def get_consequent_slim(self, user_id, rule_id, device_id):
        try:
            dto = SwitchConsequent()
            key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_consequents:" + device_id
            dto.device_id = device_id
            dto.device_name = self.r.get("device:" + device_id + ":name")
            dto.order = self.r.get(key_pattern + ":order")
            dto.delay = self.r.get(key_pattern + ":delay")
            return dto
        except Exception as error:
            print(repr(error))
            return "error"

    def delete_consequent(self, user_id, rule_id, device_id):
        try:
            self.r.lrem("device:" + device_id + ":rules", rule_id)
            self.r.lrem("user:" + user_id + ":rule:" + rule_id + ":device_consequents", device_id)
            key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_consequents:" + device_id
            self.r.delete(key_pattern + ":delay")
            self.r.delete(key_pattern + ":order")
            return "true"
        except Exception as error:
            print(repr(error))
            return "error"

    def add_consequent(self, user_id, rule_id, device_id):
        try:
            device_consequents = self.r.lrange("user:" + user_id + ":rule:" + rule_id + ":device_consequents")
            result = "false"
            if device_id not in device_consequents:
                consequent = SwitchConsequent()
                consequent.order = str(len(device_consequents))
                self.r.rpush("device:" + device_id + ":rules", rule_id)
                self.r.rpush("user:" + user_id + ":rule:" + rule_id + ":device_consequents", device_id)
                key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_consequents:" + device_id
                self.r.set(key_pattern + ":delay", consequent.delay)
                self.r.set(key_pattern + ":order", consequent.order)
                result = "true"
            return result
        except Exception as error:
            print(repr(error))
            return "error"

    def update_consequent(self, user_id, rule_id, new_consequent):
        try:
            consequent = SwitchConsequent()
            consequent.consequent_mapping(new_consequent)
            device_consequents = self.r.lrange("user:" + user_id + ":rule:" + rule_id + ":device_consequents")
            result = "false"
            if consequent.device_id in device_consequents:
                key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_consequents:" + consequent.device_id
                self.r.set(key_pattern + ":delay", consequent.delay)
                self.r.set(key_pattern + ":order", consequent.order)
                result = "true"
            return result
        except Exception as error:
            print(repr(error))
            return "error"

    def switch_evaluation(self, user_id, device_id):
        key_pattern = "device:" + device_id
        automatic = self.r.get(key_pattern + ":automatic")
        output = {"measure": "false"}
        if automatic == "true":
            rules = list(self.r.smembers(key_pattern + ":rules"))
            new_status = "off"
            for rule in rules:
                rule_evaluation = self.r.get("user:" + user_id + ":rule:" + rule + ":evaluation")
                if rule_evaluation == "true":
                    new_status = "on"
                    break
            if self.r.exists(key_pattern + ":measure") == 1:
                current_status = self.r.get("device:" + device_id + ":measure")
                if current_status != new_status:
                    output["measure"] = new_status
        return output
