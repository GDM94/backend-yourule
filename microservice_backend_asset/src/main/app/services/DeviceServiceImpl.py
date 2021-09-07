import json
from ruleapp.Devices.WaterLevel.WaterLevelFunctions import WaterLevelFunction
from ruleapp.Devices.Timer.TimerFunctions import TimerFunction
from ruleapp.Devices.Switch.SwitchFuntions import SwitchFunction
from ruleapp.Devices.Alert.AlertFunctions import AlertFunction


class DeviceService(object):
    def __init__(self, mqtt_client, rabbitmq, redis, config):
        self.r = redis
        self.publish_rule = config.get("RABBITMQ", "publish_rule")
        self.publish_consequent = config.get("RABBITMQ", "publish_consequent")
        self.mqtt_client = mqtt_client
        self.rabbitmq = rabbitmq
        self.EXPIRATION = config.get("REDIS", "expiration")
        self.switch_functions = SwitchFunction(redis)
        self.waterlevel_functions = WaterLevelFunction(redis)
        self.timer_functions = TimerFunction(redis)
        self.alert_functions = AlertFunction(redis)

    def device_registration(self, user_id, device_id):
        try:
            prefix = device_id.split("-")[0]
            if prefix == "SWITCH":
                self.switch_functions.register(user_id, device_id)
            elif prefix == "WATERLEVEL":
                self.waterlevel_functions.register(user_id, device_id)
            return "true"
        except Exception as error:
            print(repr(error))
            return "error"

    def device_update(self, user_id, device_id, device_json):
        try:
            prefix = device_id.split("-")[0]
            if prefix == "SWITCH":
                self.switch_functions.update_device(device_json)
            elif prefix == "WATERLEVEL":
                self.waterlevel_functions.update_device(device_json)
            elif prefix == "timer":
                self.timer_functions.update_device(device_json)
            elif prefix == "alert":
                self.alert_functions.update_device(device_json)
            return "updated"
        except Exception as error:
            print(repr(error))
            return "error"

    def delete_device(self, user_id, device_id):
        try:
            prefix = device_id.split("-")[0]
            if prefix == "SWITCH":
                self.switch_functions.delete_device(user_id, device_id)
                # trigger setting device
                self.mqtt_client.publish(device_id, "off/0")
            else:
                rules = self.r.lrange("device:" + device_id + ":rules")
                if prefix == "WATERLEVEL":
                    self.waterlevel_functions.delete_device(user_id, device_id)
                # trigger rule evaluation
                trigger_message = {"user_id": user_id, "rules": rules}
                payload = json.dumps(trigger_message)
                self.rabbitmq.publish(self.publish_rule, payload)
            return "deleted"
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
                output.append(device_name)
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
                output.append(device_name)
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
                rules = list(self.r.smembers("device:" + device_id + ":rules"))
                trigger = {"user_id": user_id, "rule_id": ""}
                for rule in rules:
                    trigger["rule_id"] = rule
                    payload = json.dumps(trigger)
                    self.rabbitmq.publish(self.publish_consequent, payload)
            return "true"
        except Exception as error:
            print(repr(error))
            return "error"

    def set_consequent_manual_measure(self, device_id, manual_measure):
        try:
            self.r.set("device:" + device_id + ":manual_measure", manual_measure)
            # trigger setting device
            self.mqtt_client.publish(device_id, manual_measure + "/0")
            return "true"
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

