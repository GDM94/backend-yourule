from .AlertDTO import Alert


class AlertFunction(object):
    def __init__(self, redis):
        self.r = redis

    def register(self, user_id, email):
        try:
            device_id = "alert-" + user_id
            key_pattern = "device:" + device_id
            if self.r.exists(key_pattern + ":name") == 0:
                self.r.set(key_pattern + ":name", "alert")
                self.r.set(key_pattern + ":user_id", user_id)
                self.r.rpush(key_pattern + ":email_list", email)
                return "true"
            else:
                return "false"
        except Exception as error:
            print(repr(error))
            return "error"

    def get_device(self, user_id, device_id):
        try:
            key_pattern = "device:" + device_id
            dto = Alert()
            dto.id = device_id
            dto.name = self.r.get(key_pattern + ":name")
            dto.email_list = self.r.lrange(key_pattern + ":email_list")
            if self.r.exists(key_pattern + ":rules") == 1:
                rules_id = self.r.lrange(key_pattern + ":rules")
                for rule_id in rules_id:
                    rule_name = self.r.get("user:" + user_id + ":rule:" + rule_id + ":name")
                    dto.rules.append({"id": rule_id, "name": rule_name})
            return dto
        except Exception as error:
            print(repr(error))
            return "error"

    def delete_all_email(self, device_id):
        key_pattern = "device:" + device_id
        if self.r.exists(key_pattern + ":email_list"):
            email_list = self.r.lrange(key_pattern + ":email_list")
            if len(email_list) > 0:
                for email in email_list:
                    self.r.lrem(key_pattern + ":email_list", email)

    def update_device(self, new_device):
        try:
            dto = Alert()
            dto.device_mapping(new_device)
            key_pattern = "device:" + dto.id
            self.r.set(key_pattern + ":name", dto.name)
            self.delete_all_email(dto.id)
            if len(dto.email_list) > 0:
                for email in dto.email_list:
                    self.r.rpush(key_pattern + ":email_list", email)
            return dto
        except Exception as error:
            print(repr(error))
            return "error"

    def add_alert_email(self, user_id):
        try:
            alert_id = "alert-" + user_id
            self.r.rpush("device:" + alert_id + ":email_list", "")
            return "true"
        except Exception as error:
            print(repr(error))
            return "error"

    def delete_alert_email(self, user_id, index):
        try:
            alert_id = "alert-" + user_id
            email_list = self.r.lrange("device:" + alert_id + ":email_list")
            email = email_list[index]
            self.r.lrem("device:" + alert_id + ":email_list", email)
            return "true"
        except Exception as error:
            print(repr(error))
            return "error"

    def modify_alert_email(self, user_id, email, idx):
        try:
            alert_id = "alert-" + user_id
            self.r.lset("device:" + alert_id + ":email_list", idx, email)
            return "true"
        except Exception as error:
            print(repr(error))
            return "error"
