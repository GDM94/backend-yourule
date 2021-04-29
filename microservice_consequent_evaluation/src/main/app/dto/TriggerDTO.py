
class Trigger(object):
    def __init__(self, user_id, device_id, measure, setting, rules):
        self.user_id = user_id
        self.device_id = device_id
        self.measure = measure
        self.setting = setting
        self.rules = rules

