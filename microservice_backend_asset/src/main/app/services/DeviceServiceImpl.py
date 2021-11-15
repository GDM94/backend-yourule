from ruleapp.Devices.WaterLevel.WaterLevelFunctions import WaterLevelFunction
from ruleapp.Devices.Timer.TimerFunctions import TimerFunction
from ruleapp.Devices.Switch.SwitchFuntions import SwitchFunction
from ruleapp.Devices.Alert.AlertFunctions import AlertFunction
from ruleapp.Devices.Button.ButtonFunctions import ButtonFunction
import json


class DeviceService(object):
    def __init__(self, mqtt_client, rabbitmq, redis, config):
        self.r = redis
        self.publish_rule = config.get("RABBITMQ", "publish_rule")
        self.publish_consequent = config.get("RABBITMQ", "publish_consequent")
        self.mqtt_client = mqtt_client
        self.rabbitmq = rabbitmq
        self.EXPIRATION = config.get("REDIS", "expiration")
        self.publish_topic_mqtt_switch = config.get("MQTT", "publish_setting")
        self.api_key = config.get("OPEN_WEATHER", "api_key")
        self.api_location_url = config.get("OPEN_WEATHER", "api_location_url")
        self.api_weather_url = config.get("OPEN_WEATHER", "api_weather_url")
        self.switch_functions = SwitchFunction(redis)
        self.waterlevel_functions = WaterLevelFunction(redis)
        self.timer_functions = TimerFunction(redis)
        self.alert_functions = AlertFunction(redis)
        self.button_functions = ButtonFunction(redis)

    def get_device(self, user_id, device_id):
        try:
            device = {}
            if "SWITCH" in device_id:
                device = self.switch_functions.get_device(user_id, device_id)
            elif "WATERLEVEL" in device_id:
                device = self.waterlevel_functions.get_device(user_id, device_id)
            elif "timer" in device_id:
                device = self.timer_functions.get_device(user_id, device_id)
            elif "alert" in device_id:
                device = self.alert_functions.get_device(user_id, device_id)
            elif "BUTTON" in device_id:
                device = self.button_functions.get_device(user_id, device_id)
            return device
        except Exception as error:
            print(repr(error))
            return "error"

    def device_registration(self, user_id, device_id):
        try:
            if "SWITCH" in device_id:
                return self.switch_functions.register(user_id, device_id)
            elif "WATERLEVEL" in device_id:
                return self.waterlevel_functions.register(user_id, device_id)
            elif "BUTTON" in device_id:
                return self.button_functions.register(user_id, device_id)
        except Exception as error:
            print(repr(error))
            return "error"

    def device_update(self, device_id, new_device):
        try:
            if "SWITCH" in device_id:
                self.switch_functions.update_device(new_device)
            elif "WATERLEVEL" in device_id:
                self.waterlevel_functions.update_device(new_device)
            elif "timer" in device_id:
                self.timer_functions.update_device(new_device)
            elif "alert" in device_id:
                self.alert_functions.update_device(new_device)
            elif "BUTTON" in device_id:
                self.button_functions.update_device(new_device)
            return "true"
        except Exception as error:
            print(repr(error))
            return "error"

    def delete_device(self, user_id, device_id):
        try:
            if "SWITCH" in device_id:
                self.switch_functions.delete_device(user_id, device_id)
                # trigger setting device
                self.mqtt_client.publish(device_id, "off/0")
            else:
                rules = self.r.lrange("device:" + device_id + ":rules")
                if "WATERLEVEL" in device_id:
                    self.waterlevel_functions.delete_device(user_id, device_id)
                if "BUTTON" in device_id:
                    self.button_functions.delete_device(user_id, device_id)
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
                # trigger consequent evaluation
                rules = self.r.lrange("device:" + device_id + ":rules")
                trigger = {"user_id": user_id, "rule_id": ""}
                for rule in rules:
                    print(rule)
                    trigger["rule_id"] = rule
                    payload = json.dumps(trigger)
                    self.rabbitmq.publish(self.publish_consequent, payload)
            return self.switch_functions.get_device(user_id, device_id)
        except Exception as error:
            print(repr(error))
            return "error"

    def set_consequent_manual_measure(self, user_id, device_id, manual_measure):
        try:
            self.r.set("device:" + device_id + ":manual_measure", manual_measure)
            # trigger setting device
            message = manual_measure + "/0"
            topic = self.publish_topic_mqtt_switch + device_id
            self.mqtt_client.publish(topic, message)
            return self.switch_functions.get_device(user_id, device_id)
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
