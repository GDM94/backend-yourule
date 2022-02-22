from ..components.Devices.DeviceId import TIMER, ALERT, WEATHER, WATER_LEVEL, SWITCH, PHOTOCELL, BUTTON, SERVO
import json
import requests
from flask import current_app as app


class DeviceService(object):
    def __init__(self, redis, config):
        self.r = redis
        self.EXPIRATION = config.get("REDIS", "expiration")
        self.mqtt_switch = config.get("MQTT", "mqtt_switch")
        self.mqtt_servo = config.get("MQTT", "mqtt_servo")
        self.endpoint_mqtt = config.get("MQTT", "endpoint_mqtt")

    def get_device(self, user_id, device_id):
        try:
            device = {}
            if SWITCH in device_id:
                device = app.switch_functions.get_device(user_id, device_id)
            elif WATER_LEVEL in device_id:
                device = app.waterlevel_functions.get_device(user_id, device_id)
            elif TIMER in device_id:
                device = app.timer_functions.get_device(user_id, device_id)
            elif ALERT in device_id:
                device = app.alert_functions.get_device(user_id, device_id)
            elif BUTTON in device_id:
                device = app.button_functions.get_device(user_id, device_id)
            elif WEATHER in device_id:
                device = app.weather_functions.get_device(user_id, device_id)
            elif PHOTOCELL in device_id:
                device = app.photocell_functions.get_device(user_id, device_id)
            elif SERVO in device_id:
                device = app.servo_functions.get_device(user_id, device_id)
            return device
        except Exception as error:
            print(repr(error))
            return "error"

    def get_device_slim(self, device_id):
        try:
            device = {}
            if SWITCH in device_id:
                device = app.switch_functions.get_device_slim(device_id)
            elif WATER_LEVEL in device_id:
                device = app.waterlevel_functions.get_device_slim(device_id)
            elif TIMER in device_id:
                device = app.timer_functions.get_device_slim(device_id)
            elif ALERT in device_id:
                device = app.alert_functions.get_device_slim(device_id)
            elif BUTTON in device_id:
                device = app.button_functions.get_device_slim(device_id)
            elif WEATHER in device_id:
                device = app.weather_functions.get_device_slim(device_id)
            elif PHOTOCELL in device_id:
                device = app.photocell_functions.get_device_slim(device_id)
            elif SERVO in device_id:
                device = app.servo_functions.get_device_slim(device_id)
            return device
        except Exception as error:
            print(repr(error))
            return "error"

    def get_device_measure(self, device_id):
        if SWITCH in device_id:
            device = app.switch_functions.get_measure(device_id)
        elif WATER_LEVEL in device_id:
            device = app.waterlevel_functions.get_measure(device_id)
        elif TIMER in device_id:
            device = app.timer_functions.get_measure()
        elif BUTTON in device_id:
            device = app.button_functions.get_measure(device_id)
        elif PHOTOCELL in device_id:
            device = app.photocell_functions.get_measure(device_id)
        elif SERVO in device_id:
            device = app.servo_functions.get_measure(device_id)
        else:
            device = {"measure": "false"}
        return device

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
                app.switch_functions.update_device(new_device)
            elif WATER_LEVEL in device_id:
                app.waterlevel_functions.update_device(new_device)
            elif TIMER in device_id:
                app.timer_functions.update_device(new_device)
            elif ALERT in device_id:
                app.alert_functions.update_device(new_device)
            elif BUTTON in device_id:
                app.button_functions.update_device(new_device)
            elif WEATHER in device_id:
                app.weather_functions.update_device(new_device)
            elif PHOTOCELL in device_id:
                app.photocell_functions.update_device(new_device)
            elif SERVO in device_id:
                app.servo_functions.update_device(new_device)
            return "true"
        except Exception as error:
            print(repr(error))
            return "error"

    def delete_device(self, user_id, device_id):
        try:
            if SWITCH in device_id:
                app.switch_functions.delete_device(user_id, device_id)
                # trigger setting device
                url = self.endpoint_mqtt + self.mqtt_switch + device_id
                message = {"message": "off/0"}
                requests.post(url, json.dumps(message))
            elif SERVO in device_id:
                off_status = self.r.get("device:" + device_id + ":setting_off")
                app.servo_functions.delete_device(user_id, device_id)
                url = self.endpoint_mqtt + self.mqtt_servo + device_id
                message = {"message": off_status + "/0"}
                requests.post(url, json.dumps(message))
            else:
                rules = self.r.lrange("device:" + device_id + ":rules")
                if WATER_LEVEL in device_id:
                    app.waterlevel_functions.delete_device(user_id, device_id)
                elif BUTTON in device_id:
                    app.button_functions.delete_device(user_id, device_id)
                elif PHOTOCELL in device_id:
                    app.photocell_functions.delete_device(user_id, device_id)
                # trigger rule evaluation
                app.rule_evaluation_service.rules_evaluation(user_id, rules)
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

    def get_all_devices(self, user_id):
        try:
            device_id_keys = self.r.lrange("user:" + user_id + ":devices")
            device_id_keys.insert(0, "timer-" + user_id)
            device_id_keys.insert(1, "WEATHER-" + user_id)
            device_id_keys.insert(2, "alert-" + user_id)
            output = []
            for device_id in device_id_keys:
                device = self.get_device_slim(device_id)
                output.append({"id": device_id, "name": device.name, "type": device.type, "color": device.color})
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
                for rule in rules:
                    app.consequent_evaluation_service.consequent_evaluation(user_id, rule)
            dto = {}
            if SWITCH in device_id:
                dto = app.switch_functions.get_device(user_id, device_id)
            elif SERVO in device_id:
                dto = app.servo_functions.get_device(user_id, device_id)
            return dto
        except Exception as error:
            print(repr(error))
            return "error"

    def set_consequent_manual_measure(self, user_id, device_id, manual_measure):
        try:
            print(device_id)
            dto = {}
            if SWITCH in device_id:
                message = app.switch_functions.set_manual_measure(user_id, device_id, manual_measure)
                url = self.endpoint_mqtt + self.mqtt_switch + device_id
                msg = {"message": message}
                requests.post(url, json.dumps(msg))
                dto = app.switch_functions.get_device(user_id, device_id)
            elif SERVO in device_id:
                message = app.servo_functions.set_manual_measure(user_id, device_id, manual_measure)
                url = self.endpoint_mqtt + self.mqtt_servo + device_id
                print(url)
                msg = {"message": message}
                requests.post(url, json.dumps(msg))
                dto = app.servo_functions.get_device(user_id, device_id)
            if dto.measure != "-":
                dto.measure = manual_measure
            return dto
        except Exception as error:
            print(repr(error))
            return "error"

    def add_alert_email(self, user_id):
        return app.alert_functions.add_alert_email(user_id)

    def delete_alert_email(self, user_id, index):
        return app.alert_functions.delete_alert_email(user_id, index)

    def modify_alert_email(self, user_id, email, idx):
        return app.alert_functions.modify_alert_email(user_id, email, idx)

    def get_device_rules(self, user_id, device_id):
        try:
            output = list(self.r.smembers("device:" + device_id + ":rules"))
            return output
        except Exception as error:
            print(repr(error))
            return "error"
