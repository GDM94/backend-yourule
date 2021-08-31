from .WaterLevelDTO import WaterLevel


class WaterLevelFunction(object):
    def __init__(self, redis):
        self.r = redis

    def register(self, user_id, device_id):
        try:
            if self.r.exists("device:" + device_id + ":name") == 0:
                key_pattern = "device:" + device_id
                device_id_keys = self.r.lrange("user:" + user_id + ":sensors")
                device_name = "WATERLEVEL" + str(len(device_id_keys))
                self.r.set(key_pattern + ":name", device_name)
                return "true"
            else:
                return "false"
        except Exception as error:
            print(repr(error))
            return "error"

    def get_device(self, device_id):
        try:
            key_pattern = "device:" + device_id
            dto = WaterLevel()
            dto.device_id = device_id
            dto.name = self.r.get(key_pattern + ":name")
            if self.r.exists(key_pattern + ":rules") == 1:
                dto.rules = self.r.lrange(key_pattern + ":rules")
            if self.r.exists(key_pattern + ":measure") == 1:
                dto.measure = self.r.get(key_pattern + ":measure")
                dto.absolute_measure = self.r.get(key_pattern + ":absolute_measure")
                dto.color = "green"
                dto.status = "connected"
            else:
                dto.measure = "-"
                dto.absolute_measure = "-"
                dto.color = "red"
                dto.status = "disconnected"
            dto.setting_max = self.r.get(key_pattern + ":setting:max")
            dto.setting_error = self.r.get(key_pattern + ":setting:error")
            dto.max_measure = self.r.get(key_pattern + ":max_measure")
            dto.max_measure_time = self.r.get(key_pattern + ":max_measure_time")
            dto.min_measure = self.r.get(key_pattern + ":min_measure")
            dto.min_measure_time = self.r.get(key_pattern + ":min_measure_time")
            return dto
        except Exception as error:
            print(repr(error))
            return "error"

    def get_device_slim(self, device_id):
        try:
            dto = WaterLevel()
            dto.device_id = device_id
            dto.name = self.r.get("device:" + device_id + ":name")
            return dto
        except Exception as error:
            print(repr(error))
            return "error"

    def update_device(self, dto):
        try:
            key_pattern = "device:" + dto.device_id
            self.r.set(key_pattern + ":name", dto.name)
            self.r.set(key_pattern + ":setting:max", dto.setting_max)
            self.r.set(key_pattern + ":setting:error", dto.setting_error)
            self.r.set(key_pattern + ":measure", dto.measure)
            return dto
        except Exception as error:
            print(repr(error))
            return "error"

    def add_rule(self, device_id, rule_id):
        try:
            self.r.rpush("device:" + device_id + ":rules", rule_id)
            return "true"
        except Exception as error:
            print(repr(error))
            return "error"

    def delete_rule(self, device_id, rule_id):
        try:
            self.r.lrem("device:" + device_id + ":rules", rule_id)
            return "true"
        except Exception as error:
            print(repr(error))
            return "error"

    def delete_device(self, user_id, device_id):
        self.r.lrem("user:" + user_id + ":sensors", device_id)
        key_pattern = "device:" + device_id
        self.r.delete(key_pattern + ":name")
        self.r.delete(key_pattern + ":measure")
        self.r.delete(key_pattern + ":absolute_measure")
        self.r.delete(key_pattern + ":setting:max")
        self.r.delete(key_pattern + ":setting:error")
        self.r.delete(key_pattern + ":max_measure")
        self.r.delete(key_pattern + ":max_measure_time")
        self.r.delete(key_pattern + ":min_measure")
        self.r.delete(key_pattern + ":min_measure_time")