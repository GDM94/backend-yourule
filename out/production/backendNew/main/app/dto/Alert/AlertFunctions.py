class AlertFunction(object):
    def __init__(self, redis):
        self.r = redis

    def register(self, alert_dto):
        key_pattern = "device:"+alert_dto
        if self.r.exists(key_pattern+":name") == 0:
            self.r.set(key_pattern+":name", alert_dto.name)
            self.r.rpush(key_pattern+":email_list", alert_dto.email_list[0])
