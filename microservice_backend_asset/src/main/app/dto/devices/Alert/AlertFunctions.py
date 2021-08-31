from .AlertDTO import Alert


class AlertFunction(object):
    def __init__(self, redis):
        self.r = redis

    def register(self, user_id, email):
        try:
            device_id = "alert" + user_id
            key_pattern = "device:" + device_id
            if self.r.exists(key_pattern + ":name") == 0:
                self.r.set(key_pattern + ":name", "alert")
                self.r.rpush(key_pattern + ":email_list", email)
                return "true"
            else:
                return "false"
        except Exception as error:
            print(repr(error))
            return "error"

    def get_device(self, device_id):
        try:
            dto = Alert()
            key_pattern = "device:" + dto.device_id
            dto.device_id = device_id
            dto.name = self.r.get(key_pattern + ":name")
            dto.email_list = self.r.lrange(key_pattern + ":email_list")
            dto.rules = self.r.lrange(key_pattern + ":rules")
            return dto
        except Exception as error:
            print(repr(error))
            return "error"

    def get_device_slim(self, device_id):
        try:
            dto = Alert()
            key_pattern = "device:" + dto.device_id
            dto.device_id = device_id
            dto.name = self.r.get(key_pattern + ":name")
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

    def update_device(self, dto):
        try:
            key_pattern = "device:" + dto.device_id
            self.r.set(key_pattern + ":name", dto.name)
            self.delete_all_email(dto.device_id)
            if len(dto.email_list) > 0:
                for email in dto.email_list:
                    self.r.rpush(key_pattern + ":email_list", email)
            return dto
        except Exception as error:
            print(repr(error))
            return "error"
