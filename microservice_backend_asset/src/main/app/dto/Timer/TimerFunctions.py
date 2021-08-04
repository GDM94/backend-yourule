from .TimerDTO import Timer
from .TimerAntecedentDTO import TimerAntecedent
from datetime import datetime


class TimerFunction(object):
    def __init__(self, redis):
        self.r = redis

    def register(self, dto):
        try:
            if self.r.exists("device:" + dto.device_id + ":name") == 0:
                key_pattern = "device:" + dto.device_id
                self.r.set(key_pattern+":name", dto.name)
                return "true"
            else:
                return "false"
        except Exception as error:
            print(repr(error))
            return "error"

    def get_device(self, device_id):
        try:
            dto = Timer()
            dto.name = self.r.get("device:" + device_id + ":name")
            if self.r.exists("device:" + device_id + ":rules") == 1:
                dto.rules = self.r.lrange("device:" + device_id + ":rules")
            dto.measure_time = datetime.now().strftime("%H:%M")
            dto.measure_day = str(datetime.today().weekday())
            return dto
        except Exception as error:
            print(repr(error))
            return "error"

    def get_device_slim(self, device_id):
        try:
            dto = Timer()
            dto.name = self.r.get("device:" + device_id + ":name")
            return dto
        except Exception as error:
            print(repr(error))
            return "error"

    def update_device(self, dto):
        try:
            key_pattern = "device:" + dto.device_id
            self.r.set(key_pattern+":name", dto.name)
            return dto
        except Exception as error:
            print(repr(error))
            return "error"

    def add_rule(self, device_id, rule_id):
        try:
            self.r.rpush("device:" + device_id+":rules", rule_id)
            return "true"
        except Exception as error:
            print(repr(error))
            return "error"

    def delete_rule(self,  device_id, rule_id):
        try:
            self.r.lrem("device:" + device_id+":rules", rule_id)
            return "true"
        except Exception as error:
            print(repr(error))
            return "error"







