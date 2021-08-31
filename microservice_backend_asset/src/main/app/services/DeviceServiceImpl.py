from ..dto.AlertConsequentDTO import AlertConsequent
from ..dto.DeviceAntecedentDTO import DeviceAntecedent
from ..dto.DeviceConsequentDTO import DeviceConsequent
import json
from datetime import datetime


class DeviceService(object):
    def __init__(self, mqtt_client, rabbitmq, redis, config):
        self.r = redis
        self.publish_rule = config.get("RABBITMQ", "publish_rule")
        self.publish_consequent = config.get("RABBITMQ", "publish_consequent")
        self.mqtt_client = mqtt_client
        self.rabbitmq = rabbitmq
        self.EXPIRATION = config.get("REDIS", "expiration")

    def device_registration(self, user_id, device_id):
        try:
            key_pattern = "device:" + device_id
            if self.r.exists(key_pattern + ":userid") == 0:
                self.r.set(key_pattern + ":user_id", user_id)
                self.r.setex(key_pattern + ":measure", "init")
                self.r.setex(key_pattern + ":absolute_measure", "init")
                timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                self.r.set(key_pattern + ":registration_date", timestamp)
                prefix = device_id.split("-")[0]
                if prefix == "SWITCH":
                    self.r.rpush("user:" + user_id + ":consequents", device_id)
                    self.r.set(key_pattern + ":last_on", timestamp)
                    self.r.set(key_pattern + ":last_off", timestamp)
                    self.r.set(key_pattern + ":automatic", "true")
                    self.r.set(key_pattern + ":manual_measure", "off")
                else:
                    self.r.rpush("user:" + user_id + ":antecedents", device_id)
                    self.r.set(key_pattern + ":min_measure", "-")
                    self.r.set(key_pattern + ":min_measure_time", "-")
                    self.r.set(key_pattern + ":max_measure", "-")
                    self.r.set(key_pattern + ":max_measure_time", "-")
                    if prefix == "PHOTOCELL":
                        self.device_update_setting(device_id, "1024", "0")
                    elif prefix == "WATERLEVEL":
                        self.device_update_setting(device_id, "100", "0")
                    elif prefix == "SOILMOISTURE":
                        self.device_update_setting(device_id, "1024", "0")
                    elif prefix == "AMMETER":
                        self.device_update_setting(device_id, "100", "0")
                    elif prefix == "BUTTON":
                        self.device_update_setting(device_id, "", "")
                output = "true"
            else:
                output = "false"
        except Exception as error:
            print(repr(error))
            return "error"
        else:
            return output

    def device_update_setting(self, device_id, max_measure, error_setting):
        try:
            key_pattern = "device:" + device_id
            self.r.set(key_pattern + ":setting:max", max_measure)
            self.r.set(key_pattern + ":setting:error", error_setting)
            measure = "null"
            if self.r.exists(key_pattern + ":absolute_measure"):
                absolute_measure = self.r.get(key_pattern + ":absolute_measure")
                measure = self.device_antecedent_measure(device_id, absolute_measure)
                self.r.setex(key_pattern + ":measure", measure)
            output = measure
        except Exception as error:
            print(repr(error))
            return "error"
        else:
            return output

    def device_antecedent_measure(self, device_id, measure):
        if "SWITCH" not in device_id:
            if measure != "init":
                key_pattern = "device:" + device_id
                if "WATERLEVEL" in device_id:
                    max_measure = int(self.r.get(key_pattern + ":setting:max"))
                    error_setting = int(self.r.get(key_pattern + ":setting:error"))
                    relative_measure = float(measure) - float(error_setting)
                    measure = str(round((1 - (relative_measure / float(max_measure))) * 100.0))
                elif "PHOTOCELL" in device_id or "SOILMOISTURE" in device_id:
                    max_measure = 1024
                    measure = str(round((int(measure) / max_measure) * 100.0))
                elif "AMMETER" in device_id:
                    max_measure = int(self.r.get(key_pattern + ":setting:max"))
                    measure = str(round((int(measure) / max_measure) * 100.0))
        return measure

    def device_update_name(self, device_id, device_name):
        try:
            self.r.set("device:" + device_id + ":name", device_name)
            output = "settings of device {} successful updated".format(device_id)
        except Exception as error:
            print(repr(error))
            return "error"
        else:
            return output

    def get_user_antecedent_list(self, user_id):
        try:
            output = []
            device_id_keys = self.r.lrange("user:" + user_id + ":sensors")
            device_id_keys.insert(0, "timer" + user_id)
            for device_id in device_id_keys:
                key_pattern = "device:" + device_id
                device_name = self.r.get(key_pattern + ":name")
                output.append(device_name)
        except Exception as error:
            print(repr(error))
            return "error"
        else:
            return output

    def get_user_consequent_list(self, user_id):
        try:
            device_id_keys = self.r.lrange("user:" + user_id + ":switches")
            device_id_keys.insert(0, "alert" + user_id)
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

    def delete_device(self, user_id, device_id):
        try:
            key_pattern = "device:" + device_id
            if "SWITCH" in device_id:
                self.r.lrem("user:" + user_id + ":consequents", device_id)
                self.r.delete(key_pattern + ":last_on")
                self.r.delete(key_pattern + ":last_off")
                self.r.delete(key_pattern + ":automatic")
            else:
                self.r.lrem("user:" + user_id + ":antecedents", device_id)
                self.r.delete(key_pattern + ":max_measure")
                self.r.delete(key_pattern + ":min_measure")
                self.r.delete(key_pattern + ":max_measure_time")
                self.r.delete(key_pattern + ":min_measure_time")
                self.r.delete(key_pattern + ":setting:max")
                self.r.delete(key_pattern + ":setting:error")

            self.delete_device_rules(user_id, device_id)
            self.r.delete(key_pattern + ":userid")
            self.r.delete(key_pattern + ":name")
            self.r.delete(key_pattern + ":measure")
            self.r.delete(key_pattern + ":absolute_measure")
            self.r.delete(key_pattern + ":rules")
        except Exception as error:
            print(repr(error))
            return "error"
        else:
            return "deleted"

    def delete_device_rules(self, user_id, device_id):
        key_pattern = "device:" + device_id
        if self.r.exists(key_pattern + ":rules"):
            rules = list(self.r.smembers(key_pattern + ":rules"))
            if len(rules) > 0:
                if "SWITCH" in device_id:
                    for rule_id in rules:
                        self.r.delete(
                            "user:" + user_id + ":rule:" + rule_id + ":consequent:" + device_id + ":if_value")
                        self.r.delete(
                            "user:" + user_id + ":rule:" + rule_id + ":consequent:" + device_id + ":else_value")
                    # trigger setting device
                    self.mqtt_client.publish(device_id, "off/0")
                else:
                    for rule_id in rules:
                        self.r.delete(
                            "user:" + user_id + ":rule:" + rule_id + ":antecedent:" + device_id + ":start_value")
                        self.r.delete(
                            "user:" + user_id + ":rule:" + rule_id + ":antecedent:" + device_id + ":stop_value")
                        self.r.delete(
                            "user:" + user_id + ":rule:" + rule_id + ":antecedent:" + device_id + ":condition")
                        self.r.delete(
                            "user:" + user_id + ":rule:" + rule_id + ":antecedent:" + device_id + ":evaluation")
                    # trigger rule evaluation
                    trigger_message = {"user_id": user_id, "rules": rules}
                    payload = json.dumps(trigger_message)
                    self.rabbitmq.publish(self.publish_rule, payload)

    def device_update(self, device_id, device_name, max_measure, error_setting):
        try:
            self.device_update_name(device_id, device_name)
            if max_measure != "":
                self.device_update_setting(device_id, max_measure, error_setting)

        except Exception as error:
            print(repr(error))
            return "error"
        else:
            return "updated"

    def get_device_measure(self, device_id):
        try:
            if self.r.exists("device:" + device_id + ":measure"):
                output = self.r.get("device:" + device_id + ":measure")
            else:
                output = "null"
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
        except Exception as error:
            print(repr(error))
            return "error"
        else:
            output = self.get_consequent_device(user_id, device_id)
            return output

    def set_consequent_manual_measure(self, device_id, manual_measure):
        try:
            self.r.set("device:" + device_id + ":manual_measure", manual_measure)
            # trigger setting device
            self.mqtt_client.publish(device_id, manual_measure + "/0")
        except Exception as error:
            print(repr(error))
            return "error"
        else:
            return "set"

    def get_all_devices_id(self):
        try:
            keys = self.r.scan("device:*:userid")
            id_list = []
            for key in keys:
                device_id = key.split(":")[1]
                id_list.append(device_id)
        except Exception as error:
            print(repr(error))
            return "error"
        else:
            return {"id_list": id_list}

    def add_alert_email(self, user_id):
        try:
            alert_id = "alert" + user_id
            self.r.rpush("device:" + alert_id + ":email_list", "")
        except Exception as error:
            print(repr(error))
            return "error"
        else:
            return "added"

    def delete_alert_email(self, user_id, index):
        try:
            alert_id = "alert" + user_id
            email_list = self.r.lrange("device:" + alert_id + ":email_list")
            email = email_list[index]
            self.r.lrem("device:" + alert_id + ":email_list", email)
        except Exception as error:
            print(repr(error))
            return "error"
        else:
            return "deleted"

    def modify_alert_email(self, user_id, email, idx):
        try:
            alert_id = "alert" + user_id
            self.r.lset("device:" + alert_id + ":email_list", idx, email)
        except Exception as error:
            print(repr(error))
            return "error"
        else:
            return "deleted"
