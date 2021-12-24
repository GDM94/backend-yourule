from ruleapp.Devices.DeviceEvaluationDTO import DeviceEvaluation
from ruleapp.Devices.WaterLevel.WaterLevelFunctions import WaterLevelFunction
from ruleapp.Devices.Button.ButtonFunctions import ButtonFunction
from ruleapp.Devices.Switch.SwitchFuntions import SwitchFunction
from ruleapp.Devices.Photocell.PhotocellFunctions import PhotocellFunction
from ruleapp.Devices.Servo.ServoFunctions import ServoFunction
from ruleapp.Devices.DeviceId import SWITCH, WATER_LEVEL, BUTTON, PHOTOCELL, SERVO


class DeviceServiceEvaluation(object):
    def __init__(self, redis):
        self.r = redis
        self.waterlevel_functions = WaterLevelFunction(redis)
        self.switch_functions = SwitchFunction(redis)
        self.button_functions = ButtonFunction(redis)
        self.photocell_functions = PhotocellFunction(redis)
        self.servo_functions = ServoFunction(redis)

    def measure_evaluation(self, device_id, measure):
        output = DeviceEvaluation()
        try:
            if self.r.exists("device:" + device_id + ":user_id") == 1:
                if SWITCH in device_id:
                    output = self.switch_functions.device_evaluation(device_id, measure)
                elif WATER_LEVEL in device_id:
                    output = self.waterlevel_functions.device_evaluation(device_id, measure)
                elif BUTTON in device_id:
                    output = self.button_functions.device_evaluation(device_id, measure)
                elif PHOTOCELL in device_id:
                    output = self.photocell_functions.device_evaluation(device_id, measure)
                elif SERVO in device_id:
                    self.servo_functions.device_evaluation(device_id, measure)
            return output
        except Exception as error:
            print(repr(error))
            return output

    def expiration_evaluation(self, device_id, expiration):
        try:
            if self.r.exists("device:" + device_id + ":expiration") == 1:
                device_expiration = self.r.get("device:" + device_id + ":expiration")
                if device_expiration != expiration:
                    return device_expiration
                else:
                    return "false"
            else:
                return "false"
        except Exception as error:
            print(repr(error))
            return "false"

    def check_device_registration(self, device_id):
        if self.r.exists("device:" + device_id + ":name") == 0:
            keys_id = device_id.split("-")
            hardware_id = keys_id[-1]
            if self.r.exists("device:" + hardware_id + ":user") == 1:
                user_id = self.r.get("device:" + hardware_id + ":user")
                self.device_registration(user_id, device_id)

    def device_registration(self, user_id, device_id):
        try:
            if SWITCH in device_id:
                self.switch_functions.register(user_id, device_id)
            elif WATER_LEVEL in device_id:
                self.waterlevel_functions.register(user_id, device_id)
            elif BUTTON in device_id:
                self.button_functions.register(user_id, device_id)
            elif PHOTOCELL in device_id:
                self.photocell_functions.register(user_id, device_id)
            elif SERVO in device_id:
                self.servo_functions.register(user_id, device_id)
            print(device_id + " registered!")
        except Exception as error:
            print(repr(error))
