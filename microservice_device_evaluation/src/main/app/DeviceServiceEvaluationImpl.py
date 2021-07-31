from .dto.TriggerDTO import Trigger
from datetime import datetime


class DeviceServiceEvaluation(object):
    def __init__(self, redis):
        self.r = redis

    def device_antecedent_measure(self, device_id, absolute_measure, timestamp):
        measure = absolute_measure
        if "SWITCH" not in device_id:
            key_pattern = "device:" + device_id
            if "WATERLEVEL" in device_id:
                max_measure = int(self.r.get(key_pattern + ":setting:max"))
                error_setting = int(self.r.get(key_pattern + ":setting:error"))
                relative_measure = float(absolute_measure) - float(error_setting)
                measure = str(round((1 - (relative_measure / float(max_measure))) * 100.0))
            elif "PHOTOCELL" in device_id or "SOILMOISTURE" in device_id:
                max_measure = 1024
                measure = str(round((int(absolute_measure) / max_measure) * 100.0))
            elif "AMMETER" in device_id:
                max_measure = int(self.r.get(key_pattern + ":setting:max"))
                measure = str(round((int(absolute_measure) / max_measure) * 100.0))
            elif "BUTTON" in device_id:
                if absolute_measure == "on":
                    self.r.set(key_pattern + ":max_measure_time", timestamp)
                else:
                    self.r.set(key_pattern + ":min_measure_time", timestamp)
        return measure

    def device_max_measure_range(self, device_id, measure, timestamp):
        try:
            if "SWITCH" not in device_id and "BUTTON" not in device_id:
                key_pattern = "device:" + device_id
                if self.r.exists(key_pattern + ":max_measure"):
                    max_measure = self.r.get(key_pattern + ":max_measure")
                    if max_measure != "-":
                        if float(measure) > float(max_measure):
                            self.r.set(key_pattern + ":max_measure", measure)
                            self.r.set(key_pattern + ":max_measure_time", timestamp)
                    else:
                        self.r.set(key_pattern + ":max_measure", measure)
                        self.r.set(key_pattern + ":max_measure_time", timestamp)
        except Exception as error:
            print(repr(error))

    def device_min_measure_range(self, device_id, measure, timestamp):
        try:
            if "SWITCH" not in device_id and "BUTTON" not in device_id:
                key_pattern = "device:" + device_id
                if self.r.exists(key_pattern + ":min_measure"):
                    min_measure = self.r.get(key_pattern + ":min_measure")
                    if min_measure != "-":
                        if float(measure) < float(min_measure):
                            self.r.set(key_pattern + ":min_measure", measure)
                            self.r.set(key_pattern + ":min_measure_time", timestamp)
                    else:
                        self.r.set(key_pattern + ":min_measure", measure)
                        self.r.set(key_pattern + ":min_measure_time", timestamp)
        except Exception as error:
            print(repr(error))

    def device_evaluation(self, device_id, measure):
        output = Trigger("", device_id, "", [], "")
        try:
            key_pattern = "device:" + device_id
            if self.r.exists(key_pattern + ":userid") == 1:
                user_id = self.r.get("device:" + device_id + ":userid")
                output.user_id = user_id
                absolute_measure = measure
                timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                measure = self.device_antecedent_measure(device_id, measure, timestamp)
                output.measure = measure
                self.device_max_measure_range(device_id, absolute_measure, timestamp)
                self.device_min_measure_range(device_id, absolute_measure, timestamp)

                if self.r.exists(key_pattern + ":expiration") == 1:
                    expiration = self.r.get("device:" + device_id + ":expiration")
                else:
                    expiration = 0
                self.r.setex(key_pattern + ":measure", measure, expiration)
                self.r.setex(key_pattern + ":absolute_measure", absolute_measure, expiration)

                rules = []
                if "SWITCH" not in device_id:
                    output.type = "antecedent"
                    if self.r.exists(key_pattern + ":rules"):
                        rules = list(self.r.smembers(key_pattern + ":rules"))
                    output.rules = rules
                else:
                    output.type = "consequent"
                    output.rules = rules
                    if measure == "on":
                        self.r.set(key_pattern + ":last_on", timestamp)
                    else:
                        self.r.set(key_pattern + ":last_off", timestamp)
        except Exception as error:
            print(repr(error))
            return output
        else:
            return output
