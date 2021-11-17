from ruleapp.Devices.DeviceEvaluationDTO import DeviceEvaluation
from ruleapp.Devices.WaterLevel.WaterLevelFunctions import WaterLevelFunction
from ruleapp.Devices.Button.ButtonFunctions import ButtonFunction
from ruleapp.Devices.Switch.SwitchFuntions import SwitchFunction


class DeviceServiceEvaluation(object):
    def __init__(self, redis):
        self.r = redis
        self.waterlevel_functions = WaterLevelFunction(redis)
        self.switch_functions = SwitchFunction(redis)
        self.button_functions = ButtonFunction(redis)

    def measure_evaluation(self, device_id, measure):
        output = DeviceEvaluation()
        try:
            if "SWITCH" in device_id:
                output = self.switch_functions.device_evaluation(device_id, measure)
            elif "WATERLEVEL" in device_id:
                output = self.waterlevel_functions.device_evaluation(device_id, measure)
            elif "BUTTON" in device_id:
                output = self.button_functions.device_evaluation(device_id, measure)
            return output
        except Exception as error:
            print(repr(error))
            return output

    def expiration_evaluation(self, device_id, expiration):
        try:
            device_expiration = self.r.get("device:" + device_id + ":expiration")
            if device_expiration != expiration:
                return device_expiration
            else:
                return "false"
        except Exception as error:
            print(repr(error))
            return "false"
