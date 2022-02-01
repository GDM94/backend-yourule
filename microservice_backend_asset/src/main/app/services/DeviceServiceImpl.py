from ruleapp.Devices.WaterLevel.WaterLevelFunctions import WaterLevelFunction
from ruleapp.Devices.Switch.SwitchFuntions import SwitchFunction
from ruleapp.Devices.Button.ButtonFunctions import ButtonFunction
from ruleapp.Devices.Timer.TimerFunctions import TimerFunction
from ruleapp.Devices.Alert.AlertFunctions import AlertFunction
from ruleapp.Devices.Weather.WeatherFunctions import WeatherFunction
from ruleapp.Devices.Photocell.PhotocellFunctions import PhotocellFunction
from ruleapp.Devices.Servo.ServoFunctions import ServoFunction
import json
import requests
from ruleapp.Devices.DeviceId import TIMER, ALERT, WEATHER, WATER_LEVEL, SWITCH, PHOTOCELL, BUTTON, SERVO


class DeviceService(object):
    def __init__(self, rabbitmq, redis, config):
        self.r = redis
        self.publish_rule = config.get("RABBITMQ", "publish_rule")
        self.publish_consequent = config.get("RABBITMQ", "publish_consequent")
        self.rabbitmq = rabbitmq
        self.EXPIRATION = config.get("REDIS", "expiration")
        self.mqtt_switch = config.get("MQTT", "mqtt_switch")
        self.mqtt_servo = config.get("MQTT", "mqtt_servo")
        self.mqtt_publisher_ip = config.get("MQTT", "ip")
        self.api_key = config.get("OPEN_WEATHER", "api_key")
        self.api_location_url = config.get("OPEN_WEATHER", "api_location_url")
        self.api_weather_url = config.get("OPEN_WEATHER", "api_weather_url")
        self.switch_functions = SwitchFunction(redis)
        self.waterlevel_functions = WaterLevelFunction(redis)
        self.button_functions = ButtonFunction(redis)
        self.timer_functions = TimerFunction(redis)
        self.alert_functions = AlertFunction(redis)
        self.weather_functions = WeatherFunction(redis, self.api_key, self.api_location_url, self.api_weather_url)
        self.photocell_functions = PhotocellFunction(redis)
        self.servo_functions = ServoFunction(redis)

    def get_device(self, user_id, device_id):
        try:
            device = {}
            if SWITCH in device_id:
                device = self.switch_functions.get_device(user_id, device_id)
            elif WATER_LEVEL in device_id:
                device = self.waterlevel_functions.get_device(user_id, device_id)
            elif TIMER in device_id:
                device = self.timer_functions.get_device(user_id, device_id)
            elif ALERT in device_id:
                device = self.alert_functions.get_device(user_id, device_id)
            elif BUTTON in device_id:
                device = self.button_functions.get_device(user_id, device_id)
            elif WEATHER in device_id:
                device = self.weather_functions.get_device(user_id, device_id)
            elif PHOTOCELL in device_id:
                device = self.photocell_functions.get_device(user_id, device_id)
            elif SERVO in device_id:
                device = self.servo_functions.get_device(user_id, device_id)
            return device
        except Exception as error:
            print(repr(error))
            return "error"

    def device_registration(self, user_id, hardware_id):
        try:
            output = "false"
            if self.r.exists("device:" + hardware_id + ":user") == 0:
                self.r.set("device:" + hardware_id + ":user", user_id)
                output = "true"
            return output
        except Exception as error:
            print(repr(error))
            return "error"

    def device_update(self, device_id, new_device):
        try:
            if SWITCH in device_id:
                self.switch_functions.update_device(new_device)
            elif WATER_LEVEL in device_id:
                self.waterlevel_functions.update_device(new_device)
            elif TIMER in device_id:
                self.timer_functions.update_device(new_device)
            elif ALERT in device_id:
                self.alert_functions.update_device(new_device)
            elif BUTTON in device_id:
                self.button_functions.update_device(new_device)
            elif WEATHER in device_id:
                self.weather_functions.update_device(new_device)
            elif PHOTOCELL in device_id:
                self.photocell_functions.update_device(new_device)
            elif SERVO in device_id:
                self.servo_functions.update_device(new_device)
            return "true"
        except Exception as error:
            print(repr(error))
            return "error"

    def delete_device(self, user_id, device_id):
        try:
            if SWITCH in device_id:
                self.switch_functions.delete_device(user_id, device_id)
                # trigger setting device
                url = self.mqtt_publisher_ip + self.mqtt_switch + device_id
                message = {"message": "off/0"}
                requests.post(url, json.dumps(message))
            elif SERVO in device_id:
                off_status = self.r.get("device:" + device_id + ":setting_off")
                self.servo_functions.delete_device(user_id, device_id)
                url = self.mqtt_publisher_ip + self.mqtt_servo + device_id
                message = {"message": off_status + "/0"}
                requests.post(url, json.dumps(message))
            else:
                rules = self.r.lrange("device:" + device_id + ":rules")
                if WATER_LEVEL in device_id:
                    self.waterlevel_functions.delete_device(user_id, device_id)
                elif BUTTON in device_id:
                    self.button_functions.delete_device(user_id, device_id)
                elif PHOTOCELL in device_id:
                    self.photocell_functions.delete_device(user_id, device_id)
                # trigger rule evaluation
                trigger_message = {"user_id": user_id, "rules": rules}
                payload = json.dumps(trigger_message)
                self.rabbitmq.publish(self.publish_rule, payload)
            return "true"
        except Exception as error:
            print(repr(error))
            return "error"

    def get_all_sensors(self, user_id):
        try:
            output = []
            device_id_keys = self.r.lrange("user:" + user_id + ":sensors")
            device_id_keys.insert(0, "timer-" + user_id)
            device_id_keys.insert(1, "WEATHER-" + user_id)
            for device_id in device_id_keys:
                key_pattern = "device:" + device_id
                device_name = self.r.get(key_pattern + ":name")
                output.append({"id": device_id, "name": device_name})
        except Exception as error:
            print(repr(error))
            return "error"
        else:
            return output

    def get_all_switches(self, user_id):
        try:
            device_id_keys = self.r.lrange("user:" + user_id + ":switches")
            device_id_keys.insert(0, "alert-" + user_id)
            output = []
            for device_id in device_id_keys:
                key_pattern = "device:" + device_id
                device_name = self.r.get(key_pattern + ":name")
                output.append({"id": device_id, "name": device_name})
        except Exception as error:
            print(repr(error))
            return "error"
        else:
            return output

    def set_consequent_automatic(self, user_id, device_id, automatic):
        try:
            self.r.set("device:" + device_id + ":automatic", automatic)
            if automatic == "true":
                rules = self.r.lrange("device:" + device_id + ":rules")
                trigger = {"user_id": user_id, "rule_id": ""}
                for rule in rules:
                    trigger["rule_id"] = rule
                    payload = json.dumps(trigger)
                    self.rabbitmq.publish(self.publish_consequent, payload)
            dto = {}
            if SWITCH in device_id:
                dto = self.switch_functions.get_device(user_id, device_id)
            elif SERVO in device_id:
                dto = self.servo_functions.get_device(user_id, device_id)
            return dto
        except Exception as error:
            print(repr(error))
            return "error"

    def set_consequent_manual_measure(self, user_id, device_id, manual_measure):
        try:
            print(device_id)
            dto = {}
            if SWITCH in device_id:
                message = self.switch_functions.set_manual_measure(user_id, device_id, manual_measure)
                url = self.mqtt_publisher_ip + self.mqtt_switch + device_id
                msg = {"message": message}
                requests.post(url, json.dumps(msg))
                dto = self.switch_functions.get_device(user_id, device_id)
            elif SERVO in device_id:
                message = self.servo_functions.set_manual_measure(user_id, device_id, manual_measure)
                url = self.mqtt_publisher_ip + self.mqtt_servo + device_id
                print(url)
                msg = {"message": message}
                requests.post(url, json.dumps(msg))
                dto = self.servo_functions.get_device(user_id, device_id)
            if dto.measure != "-":
                dto.measure = manual_measure
            return dto
        except Exception as error:
            print(repr(error))
            return "error"

    def add_alert_email(self, user_id):
        return self.alert_functions.add_alert_email(user_id)

    def delete_alert_email(self, user_id, index):
        return self.alert_functions.delete_alert_email(user_id, index)

    def modify_alert_email(self, user_id, email, idx):
        return self.alert_functions.modify_alert_email(user_id, email, idx)

    def get_device_rules(self, user_id, device_id):
        try:
            output = list(self.r.smembers("device:" + device_id + ":rules"))
            return output
        except Exception as error:
            print(repr(error))
            return "error"
