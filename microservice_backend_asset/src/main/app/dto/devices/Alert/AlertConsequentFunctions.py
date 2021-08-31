from .AlertConsequentDTO import AlertConsequent


class AlertConsequentFunction(object):
    def __init__(self, redis):
        self.r = redis

    def get_consequent(self, user_id, rule_id, device_id):
        try:
            consequent = AlertConsequent()
            key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_consequents:" + device_id
            consequent.device_name = self.r.get(key_pattern + ":device_name")
            consequent.message = self.r.get(key_pattern + ":message")
            consequent.delay = self.r.get(key_pattern + ":delay")
            consequent.order = self.r.get(key_pattern + ":order")
            return consequent
        except Exception as error:
            print(repr(error))
            return "error"

    def get_consequent_slim(self, user_id, rule_id, device_id):
        try:
            consequent = AlertConsequent()
            key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_consequents:" + device_id
            consequent.device_name = self.r.get(key_pattern + ":device_name")
            consequent.order = self.r.get(key_pattern + ":order")
            return consequent
        except Exception as error:
            print(repr(error))
            return "error"

    def delete_consequent(self, user_id, rule_id, device_id):
        try:
            self.r.lrem("user:" + user_id + ":rule:" + rule_id + ":device_consequents", device_id)
            key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_consequents:" + device_id
            self.r.delete(key_pattern + ":device_name")
            self.r.delete(key_pattern + ":message")
            self.r.delete(key_pattern + ":delay")
            self.r.delete(key_pattern + ":order")
            return "true"
        except Exception as error:
            print(repr(error))
            return "error"

    def set_consequent(self, user_id, rule_id, consequent):
        try:
            key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_consequents:" + consequent.device_id
            self.r.set(key_pattern + ":device_name", consequent.device_name)
            self.r.set(key_pattern + ":message", consequent.message)
            self.r.set(key_pattern + ":delay", consequent.delay)
            self.r.set(key_pattern + ":order", consequent.order)
            return "true"
        except Exception as error:
            print(repr(error))
            return "error"
