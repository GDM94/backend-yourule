from ..components.Devices.DeviceId import SWITCH, ALERT, SERVO
import json
import requests
from flask import current_app as app


class ConsequentEvaluationService(object):
    def __init__(self, redis, config):
        self.r = redis
        self.mqtt_switch = config.get("MQTT", "mqtt_switch")
        self.mqtt_servo = config.get("MQTT", "mqtt_servo")
        self.endpoint_mqtt = config.get("MQTT", "endpoint_mqtt")

    def consequent_evaluation(self, user_id, rule_id):
        pattern_key = "user:" + user_id + ":rule:" + rule_id
        device_consequents = self.r.lrange(pattern_key + ":device_consequents")
        alert_id = next((s for s in device_consequents if ALERT in s), "")
        if alert_id != "":
            app.alert_consequent_functions.alert_evaluation(user_id, rule_id)
        delay = 0
        for device_id in device_consequents:
            delay = delay + int(self.r.get(pattern_key + ":rule_consequents:" + device_id + ":delay"))
            if SWITCH in device_id:
                measure = app.switch_consequent_functions.switch_evaluation(user_id, device_id)
                if measure != "false":
                    url = self.endpoint_mqtt + self.mqtt_switch + device_id
                    payload = {"message": measure + "/" + str(delay)}
                    requests.post(url, json.dumps(payload))
            elif SERVO in device_id:
                measure = app.servo_consequent_functions.servo_evaluation(user_id, device_id)
                if measure != "false":
                    url = self.endpoint_mqtt + self.mqtt_servo + device_id
                    payload = {"message": measure + "/" + str(delay)}
                    requests.post(url, json.dumps(payload))
