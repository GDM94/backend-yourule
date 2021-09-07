from .dto.devices.DeviceEvaluationDTO import DeviceEvaluation
from .dto.devices.WaterLevel.WaterLevelFunctions import WaterLevelFunction
from .dto.devices.Switch.SwitchFuntions import SwitchFunction
from .dto.devices.Button.ButtonFunctions import ButtonFunction


class DeviceServiceEvaluation(object):
    def __init__(self, redis):
        self.r = redis
        self.waterlevel_functions = WaterLevelFunction(redis)
        self.switch_functions = SwitchFunction(redis)
        self.button_functions = ButtonFunction(redis)

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

    def device_evaluation(self, device_id, measure):
        output = DeviceEvaluation()
        try:
            if "SWITCH" in device_id:
                output = self.switch_functions.device_evaluation(device_id)
            elif "WATERLEVEL" in device_id:
                output = self.waterlevel_functions.device_evaluation(device_id, measure)
            elif "BUTTON" in device_id:
                output = self.button_functions.device_evaluation(device_id, measure)
            elif "PHOTOCELL" in device_id or "SOILMOISTURE" in device_id:
                output = {}
                max_measure = 1024
                # measure = str(round((int(absolute_measure) / max_measure) * 100.0))
            elif "AMMETER" in device_id:
                output = {}
                max_measure = int(self.r.get("device:" + device_id + ":setting:max"))
                # measure = str(round((int(absolute_measure) / max_measure) * 100.0))
            return output
        except Exception as error:
            print(repr(error))
            return output
