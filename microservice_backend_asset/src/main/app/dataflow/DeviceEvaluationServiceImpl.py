import json
import requests
from ..components.Devices.DeviceId import WATER_LEVEL, SWITCH, PHOTOCELL, BUTTON, SERVO
from flask import current_app as app


class DeviceEvaluationService(object):
    def __init__(self, redis, config):
        self.r = redis
        self.mqtt_switch = config.get("MQTT", "mqtt_switch")
        self.mqtt_servo = config.get("MQTT", "mqtt_servo")
        self.mqtt_expiration = config.get("MQTT", "mqtt_expiration")
        self.endpoint_mqtt = config.get("MQTT", "endpoint_mqtt")

    def device_evaluation(self, device_id, measure, expiration):
        self.check_device_registration(device_id)
        expiration_sync = self.expiration_evaluation(device_id, expiration)
        if expiration_sync != "false":
            url = self.endpoint_mqtt + self.mqtt_expiration + device_id
            payload = {"message": expiration_sync}
            requests.post(url, json.dumps(payload))
        trigger = self.measure_evaluation(device_id, measure)
        if trigger != "false" and len(trigger["rules"]) > 0:
            user_id = trigger["user_id"]
            device_id = trigger["device_id"]
            measure = trigger["measure"]
            rules = trigger["rules"]
            app.antecedent_evaluation_service.antecedent_evaluation(user_id, device_id, measure, rules)

    def measure_evaluation(self, device_id, measure):
        if WATER_LEVEL in device_id:
            return app.waterlevel_functions.device_evaluation(device_id, measure)
        elif BUTTON in device_id:
            return app.button_functions.device_evaluation(device_id, measure)
        elif PHOTOCELL in device_id:
            return app.photocell_functions.device_evaluation(device_id, measure)
        elif SERVO in device_id:
            output = app.servo_functions.device_evaluation(device_id, measure)
            if output != "false":
                url = self.endpoint_mqtt + self.mqtt_servo + device_id
                payload = {"message": output["measure"]}
                requests.post(url, json.dumps(payload))
            return "false"
        elif SWITCH in device_id:
            output = app.switch_functions.device_evaluation(device_id, measure)
            if output != "false":
                url = self.endpoint_mqtt + self.mqtt_switch + device_id
                payload = {"message": output["measure"]}
                requests.post(url, json.dumps(payload))
            return "false"

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
                app.switch_functions.register(user_id, device_id)
            elif WATER_LEVEL in device_id:
                app.waterlevel_functions.register(user_id, device_id)
            elif BUTTON in device_id:
                app.button_functions.register(user_id, device_id)
            elif PHOTOCELL in device_id:
                app.photocell_functions.register(user_id, device_id)
            elif SERVO in device_id:
                app.servo_functions.register(user_id, device_id)
            print(device_id + " registered!")
        except Exception as error:
            print(repr(error))
