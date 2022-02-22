from .WaterLevelDTO import WaterLevel
from .WaterLevelAntecedentFunctions import WaterLevelAntecedentFunction
from datetime import datetime


class WaterLevelFunction(object):
    def __init__(self, redis):
        self.r = redis
        self.waterlevel_antecedent_functions = WaterLevelAntecedentFunction(redis)

    def register(self, user_id, device_id):
        try:
            result = "false"
            key_pattern = "device:" + device_id
            if self.r.exists(key_pattern + ":name") == 0:
                self.r.rpush("user:" + user_id + ":sensors", device_id)
                self.r.rpush("user:" + user_id + ":devices", device_id)
                device = WaterLevel()
                device.id = device_id
                device_id_keys = self.r.lrange("user:" + user_id + ":sensors")
                device.name = "WATERLEVEL " + str(len(device_id_keys))
                self.r.set(key_pattern + ":name", device.name)
                self.r.set(key_pattern + ":user_id", user_id)
                self.r.set(key_pattern + ":measure", device.measure)
                self.r.set(key_pattern + ":absolute_measure", device.absolute_measure)
                self.r.set(key_pattern + ":setting:error", device.setting_error)
                self.r.set(key_pattern + ":setting:max", device.setting_max)
                self.r.set(key_pattern + ":max_measure", device.max_measure)
                self.r.set(key_pattern + ":max_measure_time", device.max_measure_time)
                self.r.set(key_pattern + ":max_measure_date", device.max_measure_date)
                self.r.set(key_pattern + ":min_measure", device.min_measure)
                self.r.set(key_pattern + ":min_measure_time", device.min_measure_time)
                self.r.set(key_pattern + ":min_measure_date", device.min_measure_date)
                self.r.set(key_pattern + ":expiration", device.expiration)
                result = device
            return result
        except Exception as error:
            print(repr(error))
            return "error"

    def get_device(self, user_id, device_id):
        try:
            key_pattern = "device:" + device_id
            dto = WaterLevel()
            dto.id = device_id
            dto.name = self.r.get(key_pattern + ":name")
            dto.setting_max = self.r.get(key_pattern + ":setting:max")
            dto.setting_error = self.r.get(key_pattern + ":setting:error")
            dto.max_measure = self.r.get(key_pattern + ":max_measure")
            dto.max_measure_time = self.r.get(key_pattern + ":max_measure_time")
            dto.max_measure_date = self.r.get(key_pattern + ":max_measure_date")
            dto.min_measure = self.r.get(key_pattern + ":min_measure")
            dto.min_measure_time = self.r.get(key_pattern + ":min_measure_time")
            dto.min_measure_date = self.r.get(key_pattern + ":min_measure_date")
            dto.expiration = self.r.get(key_pattern + ":expiration")
            if self.r.exists(key_pattern + ":rules") == 1:
                rules_id = self.r.lrange(key_pattern + ":rules")
                for rule_id in rules_id:
                    rule_name = self.r.get("user:" + user_id + ":rule:" + rule_id + ":name")
                    dto.rules.append({"id": rule_id, "name": rule_name})
            if self.r.exists(key_pattern + ":measure") == 1:
                measure = self.r.get(key_pattern + ":measure")
                if measure == "-":
                    dto.measure = measure
                    dto.absolute_measure = measure
                    dto.color = "yellow"
                    dto.status = "initialization"
                else:
                    dto.absolute_measure = self.r.get(key_pattern + ":absolute_measure")
                    relative_measure = float(dto.absolute_measure) - float(dto.setting_error)
                    dto.measure = str(round((1 - (relative_measure / float(dto.setting_max))) * 100.0))
                    dto.color = "green"
                    dto.status = "connected"
            return dto
        except Exception as error:
            print(repr(error))
            return "error"

    def get_device_slim(self, device_id):
        try:
            key_pattern = "device:" + device_id
            dto = WaterLevel()
            dto.id = device_id
            dto.name = self.r.get(key_pattern + ":name")
            if self.r.exists(key_pattern + ":measure") == 1:
                measure = self.r.get(key_pattern + ":measure")
                if measure == "-":
                    dto.measure = measure
                    dto.color = "yellow"
                    dto.status = "initialization"
                else:
                    dto.measure = measure
                    dto.color = "green"
                    dto.status = "connected"
            return dto
        except Exception as error:
            print(repr(error))
            return "error"

    def get_measure(self, device_id):
        measure = "-"
        if self.r.exists("device:" + device_id + ":measure") == 1:
            measure = self.r.get("device:" + device_id + ":measure")
        output = {"measure": measure}
        return output

    def update_device(self, new_device):
        try:
            dto = WaterLevel()
            dto.device_mapping(new_device)
            key_pattern = "device:" + dto.id
            self.r.set(key_pattern + ":name", dto.name)
            self.r.set(key_pattern + ":setting:max", dto.setting_max)
            self.r.set(key_pattern + ":setting:error", dto.setting_error)
            self.r.set(key_pattern + ":measure", dto.measure)
            self.r.set(key_pattern + ":expiration", dto.expiration)
            return dto
        except Exception as error:
            print(repr(error))
            return "error"

    def delete_device(self, user_id, device_id):
        try:
            self.r.lrem("user:" + user_id + ":sensors", device_id)
            self.r.lrem("user:" + user_id + ":devices", device_id)
            key_pattern = "device:" + device_id
            self.r.delete(key_pattern + ":name")
            self.r.delete(key_pattern + ":user_id")
            self.r.delete(key_pattern + ":measure")
            self.r.delete(key_pattern + ":absolute_measure")
            self.r.delete(key_pattern + ":setting:max")
            self.r.delete(key_pattern + ":setting:error")
            self.r.delete(key_pattern + ":max_measure")
            self.r.delete(key_pattern + ":max_measure_time")
            self.r.delete(key_pattern + ":max_measure_date")
            self.r.delete(key_pattern + ":min_measure")
            self.r.delete(key_pattern + ":min_measure_time")
            self.r.delete(key_pattern + ":min_measure_date")
            if self.r.exists(key_pattern + ":rules") == 1:
                rules = self.r.lrange(key_pattern + ":rules")
                for rule_id in rules:
                    self.waterlevel_antecedent_functions.delete_antecedent(user_id, rule_id, device_id)
            return "true"
        except Exception as error:
            print(repr(error))
            return "error"

    def measure_evaluation(self, device_id, absolute_measure):
        key_pattern = "device:" + device_id
        max_measure = int(self.r.get(key_pattern + ":setting:max"))
        error_setting = int(self.r.get(key_pattern + ":setting:error"))
        scaled_measure = float(absolute_measure) - float(error_setting)
        relative_measure = str(round((1 - (scaled_measure / float(max_measure))) * 100.0))
        expiration = int(self.r.get(key_pattern + ":expiration")) + 2
        self.r.setex(key_pattern + ":measure", expiration, relative_measure)
        self.r.setex(key_pattern + ":absolute_measure", expiration, absolute_measure)
        self.device_max_measure_range(device_id, relative_measure)
        self.device_min_measure_range(device_id, relative_measure)
        return relative_measure

    def device_max_measure_range(self, device_id, measure):
        key_pattern = "device:" + device_id
        time_str = datetime.now().strftime("%H:%M")
        date_str = datetime.now().strftime("%d/%m/%Y")
        max_measure = self.r.get(key_pattern + ":max_measure")
        if max_measure != "-":
            if float(measure) > float(max_measure):
                self.r.set(key_pattern + ":max_measure", measure)
                self.r.set(key_pattern + ":max_measure_time", time_str)
                self.r.set(key_pattern + ":max_measure_date", date_str)
        else:
            self.r.set(key_pattern + ":max_measure", measure)
            self.r.set(key_pattern + ":max_measure_time", time_str)
            self.r.set(key_pattern + ":max_measure_date", date_str)

    def device_min_measure_range(self, device_id, measure):
        key_pattern = "device:" + device_id
        time_str = datetime.now().strftime("%H:%M")
        date_str = datetime.now().strftime("%d/%m/%Y")
        min_measure = self.r.get(key_pattern + ":min_measure")
        if min_measure != "-":
            if float(measure) < float(min_measure):
                self.r.set(key_pattern + ":min_measure", measure)
                self.r.set(key_pattern + ":min_measure_time", time_str)
                self.r.set(key_pattern + ":min_measure_date", date_str)
        else:
            self.r.set(key_pattern + ":min_measure", measure)
            self.r.set(key_pattern + ":min_measure_time", time_str)
            self.r.set(key_pattern + ":min_measure_date", date_str)

    def device_evaluation(self, device_id, measure):
        output = {}
        key_pattern = "device:" + device_id
        if self.r.exists(key_pattern + ":user_id") == 0:
            return "false"
        output["user_id"] = self.r.get("device:" + device_id + ":user_id")
        output["measure"] = self.measure_evaluation(device_id, measure)
        output["device_id"] = device_id
        key_pattern = "device:" + device_id
        if self.r.exists(key_pattern + ":rules") == 0:
            return "false"
        output["rules"] = self.r.lrange(key_pattern + ":rules")
        return output
