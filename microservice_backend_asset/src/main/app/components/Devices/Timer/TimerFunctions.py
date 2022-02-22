from .TimerDTO import Timer
from datetime import datetime
from ..DeviceId import TIMER


class TimerFunction(object):
    def __init__(self, redis):
        self.r = redis

    def register(self, user_id):
        try:
            device_id = TIMER + "-" + user_id
            if self.r.exists("device:" + device_id + ":name") == 0:
                key_pattern = "device:" + device_id
                self.r.set(key_pattern + ":name", "timer")
                self.r.set(key_pattern + ":user_id", user_id)
                return "true"
            else:
                return "false"
        except Exception as error:
            print(repr(error))
            return "error"

    def get_device(self, user_id, device_id):
        try:
            key_pattern = "device:" + device_id
            dto = Timer()
            dto.id = device_id
            dto.name = self.r.get(key_pattern + ":name")
            if self.r.exists(key_pattern + ":rules") == 1:
                rules_id = self.r.lrange(key_pattern + ":rules")
                for rule_id in rules_id:
                    rule_name = self.r.get("user:" + user_id + ":rule:" + rule_id + ":name")
                    dto.rules.append({"id": rule_id, "name": rule_name})
            dto.measure_time = datetime.now().strftime("%H:%M")
            dto.measure_day = str(datetime.today().weekday())
            dto.measure = self.week_day_mapper(dto.measure_day) + ", " + dto.measure_time
            return dto
        except Exception as error:
            print(repr(error))
            return "error"

    def get_device_slim(self, device_id):
        try:
            key_pattern = "device:" + device_id
            dto = Timer()
            dto.id = device_id
            dto.name = self.r.get(key_pattern + ":name")
            return dto
        except Exception as error:
            print(repr(error))
            return "error"

    def week_day_mapper(self, number_day):
        if number_day == '0':
            return 'Lunedi'
        elif number_day == '1':
            return 'Martedi'
        elif number_day == '2':
            return 'Mercoledi'
        elif number_day == '3':
            return 'Giovedi'
        elif number_day == '4':
            return 'Venerdi'
        elif number_day == '5':
            return 'Sabato'
        elif number_day == '6':
            return 'Domenica'
        else:
            return ""

    def update_device(self, new_device):
        try:
            dto = Timer()
            dto.device_mapping(new_device)
            key_pattern = "device:" + dto.id
            self.r.set(key_pattern + ":name", dto.name)
            return dto
        except Exception as error:
            print(repr(error))
            return "error"

    def get_measure(self):
        measure_time = datetime.now().strftime("%H:%M")
        measure_day = str(datetime.today().weekday())
        measure = self.week_day_mapper(measure_day) + ", " + measure_time
        output = {"measure": measure}
        return output
