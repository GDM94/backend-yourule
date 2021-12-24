from .ServoConsequentDTO import ServoConsequent


class ServoConsequentFunction(object):
    def __init__(self, redis):
        self.r = redis

    def get_consequent(self, user_id, rule_id, device_id):
        try:
            dto = ServoConsequent()
            key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_consequents:" + device_id
            dto.device_id = device_id
            dto.device_name = self.r.get("device:" + device_id + ":name")
            dto.delay = self.r.get(key_pattern + ":delay")
            dto.order = self.r.get(key_pattern + ":order")
            dto.automatic = self.r.get("device:" + device_id + ":automatic")
            if dto.automatic == "true":
                dto.measure = self.r.get("device:" + device_id + ":measure")
            else:
                dto.measure = "manual"
            return dto
        except Exception as error:
            print(repr(error))
            return "error"

    def get_consequent_slim(self, user_id, rule_id, device_id):
        try:
            dto = ServoConsequent()
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
                consequent = ServoConsequent()
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
            consequent = ServoConsequent()
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

    def servo_evaluation(self, user_id, device_id):
        key_pattern = "device:" + device_id
        automatic = self.r.get(key_pattern + ":automatic")
        output = "false"
        if automatic == "true" and self.r.exists(key_pattern + ":measure") == 1:
            rules = self.r.lrange(key_pattern + ":rules")
            new_status = "off"
            current_status = self.r.get("device:" + device_id + ":measure")
            for rule in rules:
                rule_evaluation = self.r.get("user:" + user_id + ":rule:" + rule + ":evaluation")
                if rule_evaluation == "true":
                    new_status = "on"
                    break
            if current_status != new_status:
                if new_status == "on":
                    output = self.r.get(key_pattern + ":setting_on")
                else:
                    output = self.r.get(key_pattern + ":setting_off")
        return output
