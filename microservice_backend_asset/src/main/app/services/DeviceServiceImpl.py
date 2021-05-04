import redis
from os.path import dirname, join, abspath
import configparser

from ..dto.AlertConsequentDTO import AlertConsequent
from ..dto.DeviceAntecedentDTO import DeviceAntecedent
from ..dto.DeviceConsequentDTO import DeviceConsequent
import json
from datetime import datetime


class DeviceService(object):
    def __init__(self, mqtt_client, rabbitmq):
        config = self.read_config()
        redis_host = config.get("REDIS", "host")
        redis_port = config.get("REDIS", "port")
        self.r = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        self.publish_rule = config.get("RABBITMQ", "publish_rule")
        self.publish_consequent = config.get("RABBITMQ", "publish_consequent")
        self.publish_setting = config.get("MQTT", "publish_setting")
        self.mqtt_client = mqtt_client
        self.rabbitmq = rabbitmq
        self.EXPIRATION = config.get("REDIS", "expiration")

    def read_config(self):
        d = dirname(dirname(dirname(dirname(abspath(__file__)))))
        config_path = join(d, 'properties', 'app-config.ini')
        config = configparser.ConfigParser()
        config.read(config_path)
        return config

    def device_registration(self, user_id, device_id, device_name):
        try:
            key_pattern = "device:" + device_id
            if self.r.exists(key_pattern + ":userid") == 0:
                self.r.set(key_pattern + ":userid", user_id)
                self.r.setex(key_pattern + ":measure", self.EXPIRATION, "init")
                self.r.setex(key_pattern + ":absolute_measure", self.EXPIRATION, "init")
                self.r.set(key_pattern + ":name", device_name)
                prefix = device_id.split("-")[0]
                if prefix == "SWITCH":
                    self.r.sadd("user:" + user_id + ":consequents", device_id)
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    self.r.set(key_pattern + ":last_on", timestamp)
                    self.r.set(key_pattern + ":last_off", timestamp)
                    self.r.set(key_pattern + ":automatic", "true")
                    self.r.set(key_pattern + ":manual_measure", "off")
                else:
                    self.r.sadd("user:" + user_id + ":antecedents", device_id)
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
                output = "device {} successful registered for userId {}".format(device_id, user_id)
            else:
                output = "device {} already exist!".format(device_id)
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
                self.r.setex(key_pattern + ":measure", self.EXPIRATION, measure)
            output = measure
        except Exception as error:
            print(repr(error))
            return "error"
        else:
            return output

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
            device_id_keys = list(self.r.smembers("user:" + user_id + ":antecedents"))
            output = []
            for device_id in device_id_keys:
                device = self.get_antecedent_device_slim(user_id, device_id)
                output.append(device)
        except Exception as error:
            print(repr(error))
            return "error"
        else:
            return output

    def get_antecedent_device_slim(self, user_id, device_id):
        key_pattern = "device:" + device_id
        device_name = self.r.get(key_pattern + ":name")
        measure = "null"
        if self.r.exists(key_pattern + ":measure") == 1:
            measure = self.r.get(key_pattern + ":measure")
        return DeviceAntecedent(device_id, device_name, measure, "", "", [], measure)

    def get_antecedent_device(self, user_id, device_id):
        key_pattern = "device:" + device_id
        device_name = self.r.get(key_pattern + ":name")
        measure = "null"
        if self.r.exists(key_pattern + ":absolute_measure") == 1:
            measure = self.r.get(key_pattern + ":absolute_measure")
        max_measure = ""
        if self.r.exists(key_pattern + ":setting:max"):
            max_measure = self.r.get(key_pattern + ":setting:max")
        error_setting = ""
        if self.r.exists(key_pattern + ":setting:error"):
            error_setting = self.r.get(key_pattern + ":setting:error")
        rules = []
        if self.r.exists(key_pattern + ":rules") == 1:
            rules_id = list(self.r.smembers(key_pattern + ":rules"))
            for rule_id in rules_id:
                rule = {"id": rule_id, "name": ""}
                rule_name = self.r.get("user:" + user_id + ":rule:" + rule_id + ":name")
                rule["name"] = rule_name
                rules.append(rule)
        return DeviceAntecedent(device_id, device_name, measure, max_measure, error_setting, rules, measure)

    def get_user_consequent_list(self, user_id):
        try:
            device_id_keys = list(self.r.smembers("user:" + user_id + ":consequents"))
            output = []
            for device_id in device_id_keys:
                device = self.get_consequent_device_slim(user_id, device_id)
                output.append(device)
        except Exception as error:
            print(repr(error))
            return "error"
        else:
            return output

    def get_consequent_device_slim(self, user_id, device_id):
        key_pattern = "device:" + device_id
        device_name = self.r.get(key_pattern + ":name")
        measure = "null"
        if self.r.exists(key_pattern + ":measure"):
            measure = self.r.get(key_pattern + ":measure")
        if "alert" in device_id:
            return AlertConsequent(device_id, device_name, [], [])
        else:
            return DeviceConsequent(device_id, device_name, measure, [], "", "", "", "")

    def get_consequent_device(self, user_id, device_id):
        if "alert" in device_id:
            return self.get_alert(user_id, device_id)
        else:
            key_pattern = "device:" + device_id
            device_name = self.r.get(key_pattern + ":name")
            measure = "null"
            if self.r.exists(key_pattern + ":measure"):
                measure = self.r.get(key_pattern + ":measure")
            rules_id = list(self.r.smembers(key_pattern + ":rules"))
            rules = []
            for rule_id in rules_id:
                rule = {"id": rule_id, "name": ""}
                rule_name = self.r.get("user:" + user_id + ":rule:" + rule_id + ":name")
                rule["name"] = rule_name
                rules.append(rule)
            last_on = self.r.get(key_pattern + ":last_on")
            last_off = self.r.get(key_pattern + ":last_off")
            automatic = self.r.get(key_pattern + ":automatic")
            manual_measure = self.r.get(key_pattern + ":manual_measure")
            return DeviceConsequent(device_id, device_name, measure, rules, last_on, last_off, automatic,
                                    manual_measure)

    def get_alert(self, user_id, alert_id):
        key_pattern = "device:" + alert_id
        name = self.r.get(key_pattern + ":name")
        rules_id = list(self.r.smembers(key_pattern + ":rules"))
        rules = []
        rule = {"id": "", "name": ""}
        for rule_id in rules_id:
            rule_name = self.r.get("user:" + user_id + ":rule:" + rule_id + ":name")
            rule["id"] = rule_id
            rule["name"] = rule_name
            rules.append(rule)
        email_list = []
        if self.r.exists(key_pattern + ":email_list"):
            email_list = self.r.lrange(key_pattern + ":email_list", 0, -1)
        return AlertConsequent(alert_id, name, rules, email_list)

    def delete_device(self, user_id, device_id):
        try:
            key_pattern = "device:" + device_id
            prefix = device_id.split("-")[0]
            if prefix == "SWITCH":
                self.r.srem("user:" + user_id + ":consequents", device_id)
            else:
                self.r.srem("user:" + user_id + ":antecedents", device_id)
            if self.r.exists(key_pattern + ":rules"):
                rules = list(self.r.smembers(key_pattern + ":rules"))
                if len(rules) > 0:
                    if prefix == "SWITCH":
                        for rule_id in rules:
                            self.r.delete(
                                "user:" + user_id + ":rule:" + rule_id + ":consequent:" + device_id + ":if_value")
                            self.r.delete(
                                "user:" + user_id + ":rule:" + rule_id + ":consequent:" + device_id + ":else_value")
                        # trigger setting device
                        self.mqtt_client.publish(self.publish_setting + device_id, "off")
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
            self.r.delete(key_pattern + ":userid")
            self.r.delete(key_pattern + ":name")
            self.r.delete(key_pattern + ":measure")
            self.r.delete(key_pattern + ":setting:max")
            self.r.delete(key_pattern + ":rules")
        except Exception as error:
            print(repr(error))
            return "error"
        else:
            return "deleted"

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
            self.mqtt_client.publish(self.publish_setting + device_id, manual_measure)
        except Exception as error:
            print(repr(error))
            return "error"
        else:
            return "set"

    def get_all_devices_id(self):
        try:
            keys = self.r.scan(0, "device:*:userid", 1000)[1]
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
            email_list = self.r.lrange("device:" + alert_id + ":email_list", 0, -1)
            email = email_list[index]
            self.r.lrem("device:" + alert_id + ":email_list", 1, email)
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
