import json
from ruleapp.Rule.RuleFunctions import RuleFunction
from ruleapp.Rule.RuleDTO import Rule
from ruleapp.Devices.Timer.TimerAntecedentFunctions import TimerAntecedentFunction
from ruleapp.Devices.Alert.AlertConsequentFunctions import AlertConsequentFunction
from ruleapp.Devices.WaterLevel.WaterLevelAntecedentFunctions import WaterLevelAntecedentFunction
from ruleapp.Devices.Switch.SwitchConsequentFunctions import SwitchConsequentFunction
from ruleapp.Devices.Button.ButtonAntecedentFunctions import ButtonAntecedentFunction
from ruleapp.Devices.Switch.SwitchAntecedentFunctions import SwitchAntecedentFunction
from ruleapp.Devices.Weather.WeatherAntecedentFunctions import WeatherAntecedentFunction
from ruleapp.Devices.Photocell.PhotocellAntecedentFunctions import PhotocellAntecedentFunction
from ruleapp.Devices.Servo.ServoConsequentFunctions import ServoConsequentFunction
from ruleapp.Devices.DeviceId import TIMER, ALERT, WEATHER, WATER_LEVEL, SWITCH, PHOTOCELL, BUTTON, SERVO
import requests


class RuleService(object):
    def __init__(self, redis, config):
        self.publish_rule = config.get("RABBITMQ", "publish_rule")
        self.mqtt_switch = config.get("MQTT", "mqtt_switch")
        self.mqtt_servo = config.get("MQTT", "mqtt_servo")
        self.endpoint_mqtt = config.get("MQTT", "endpoint_mqtt")
        self.endpoint_rabbitmq = config.get("MQTT", "endpoint_rabbitmq")
        self.r = redis
        self.rule_functions = RuleFunction(redis)
        self.timer_antecedent_functions = TimerAntecedentFunction(redis)
        self.alert_consequent_functions = AlertConsequentFunction(redis)
        self.waterlevel_antecedent_functions = WaterLevelAntecedentFunction(redis)
        self.switch_consequent_functions = SwitchConsequentFunction(redis)
        self.button_antecedent_functions = ButtonAntecedentFunction(redis)
        self.switch_antecedent_functions = SwitchAntecedentFunction(redis)
        self.weather_antecedent_functions = WeatherAntecedentFunction(redis)
        self.photocell_antecedent_functions = PhotocellAntecedentFunction(redis)
        self.servo_consequent_functions = ServoConsequentFunction(redis)

    def create_rule(self, user_id, rule_name):
        try:
            rule_id = str(self.r.incr("user:" + user_id + ":rule:counter"))
            rule = Rule()
            rule.id = rule_id
            rule.name = rule_name
            key_pattern = "user:" + user_id + ":rule:" + rule_id
            self.r.rpush("user:" + user_id + ":rules", rule_id)
            self.r.set(key_pattern + ":name", rule_name)
            self.r.set(key_pattern + ":evaluation", "false")
            self.r.set(key_pattern + ":last_time_on", rule.last_time_on)
            self.r.set(key_pattern + ":last_time_off", rule.last_time_off)
            self.r.set(key_pattern + ":last_date_on", rule.last_date_on)
            self.r.set(key_pattern + ":last_date_off", rule.last_date_off)
            return rule
        except Exception as error:
            print(repr(error))
            return "error"

    def get_user_rules(self, user_id):
        try:
            rules_id_list = self.r.lrange("user:" + user_id + ":rules")
            output = []
            for rule_id in rules_id_list:
                key_pattern = "user:" + user_id + ":rule:" + rule_id
                if self.r.exists(key_pattern + ":name") == 1:
                    rule = Rule()
                    rule.name = self.r.get(key_pattern + ":name")
                    rule.id = rule_id
                    rule.evaluation = self.r.get(key_pattern + ":evaluation")
                    output.append(rule)
            return output
        except Exception as error:
            print(repr(error))
            return "error"

    def update_rule_name(self, user_id, rule_id, rule_name):
        try:
            key_pattern = "user:" + user_id + ":rule:" + rule_id
            self.r.set(key_pattern + ":name", rule_name)
            return "true"
        except Exception as error:
            print(repr(error))
            return "error"

    def add_rule_antecedent(self, user_id, rule_id, device_id):
        result = "error"
        if TIMER in device_id:
            result = self.timer_antecedent_functions.add_antecedent(user_id, rule_id, device_id)
        elif WATER_LEVEL in device_id:
            result = self.waterlevel_antecedent_functions.add_antecedent(user_id, rule_id, device_id)
        elif BUTTON in device_id:
            result = self.button_antecedent_functions.add_antecedent(user_id, rule_id, device_id)
        elif SWITCH in device_id:
            result = self.switch_antecedent_functions.add_antecedent(user_id, rule_id, device_id)
        elif WEATHER in device_id:
            result = self.weather_antecedent_functions.add_antecedent(user_id, rule_id, device_id)
        elif PHOTOCELL in device_id:
            result = self.photocell_antecedent_functions.add_antecedent(user_id, rule_id, device_id)
        if result != "error":
            result = self.get_rule_by_id(user_id, rule_id)
        return result

    def add_rule_consequent(self, user_id, rule_id, device_id):
        result = "error"
        if ALERT in device_id:
            result = self.alert_consequent_functions.add_consequent(user_id, rule_id, device_id)
        elif SWITCH in device_id:
            result = self.switch_consequent_functions.add_consequent(user_id, rule_id, device_id)
        elif SERVO in device_id:
            result = self.servo_consequent_functions.add_consequent(user_id, rule_id, device_id)
        if result != "error":
            result = self.get_rule_by_id(user_id, rule_id)
        return result

    def update_rule_antecedent(self, user_id, rule_id, device_id, antecedent_json):
        output = "error"
        if TIMER in device_id:
            output = self.timer_antecedent_functions.update_antecedent(user_id, rule_id, antecedent_json)
        elif WATER_LEVEL in device_id:
            output = self.waterlevel_antecedent_functions.update_antecedent(user_id, rule_id, antecedent_json)
        elif BUTTON in device_id:
            output = self.button_antecedent_functions.update_antecedent(user_id, rule_id, antecedent_json)
        elif SWITCH in device_id:
            output = self.switch_antecedent_functions.update_antecedent(user_id, rule_id, antecedent_json)
        elif WEATHER in device_id:
            output = self.weather_antecedent_functions.update_antecedent(user_id, rule_id, antecedent_json)
        elif PHOTOCELL in device_id:
            output = self.photocell_antecedent_functions.update_antecedent(user_id, rule_id, antecedent_json)
        if output != "error":
            output = self.get_rule_by_id(user_id, rule_id)
        return output

    def update_rule_consequent(self, user_id, rule_id, device_id, consequent_json):
        output = "error"
        if ALERT in device_id:
            output = self.alert_consequent_functions.update_consequent(user_id, rule_id, consequent_json)
        elif SWITCH in device_id:
            output = self.switch_consequent_functions.update_consequent(user_id, rule_id, consequent_json)
        elif SERVO in device_id:
            output = self.servo_consequent_functions.update_consequent(user_id, rule_id, consequent_json)
        if output != "error":
            output = self.get_rule_by_id(user_id, rule_id)
        return output

    def update_rule_consequents_order(self, user_id, rule_id, consequents_id_list):
        try:
            self.r.delete("user:" + user_id + ":rule:" + rule_id + ":device_consequents")
            order = 0
            for device_id in consequents_id_list:
                self.r.rpush("user:" + user_id + ":rule:" + rule_id + ":device_consequents", device_id)
                key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_consequents:" + device_id
                self.r.set(key_pattern + ":delay", "0")
                self.r.set(key_pattern + ":order", str(order))
                order = order + 1
            return self.get_rule_by_id(user_id, rule_id)
        except Exception as error:
            print(repr(error))
            return "error"

    def delete_rule(self, user_id, rule_id):
        try:
            key_pattern = "user:" + user_id + ":rule:" + rule_id
            self.r.lrem("user:" + user_id + ":rules", rule_id)
            self.r.delete(key_pattern + ":name")
            self.r.delete(key_pattern + ":last_time_on")
            self.r.delete(key_pattern + ":last_time_off")
            self.r.delete(key_pattern + ":last_date_on")
            self.r.delete(key_pattern + ":last_date_off")
            device_antecedents = self.r.lrange(key_pattern + ":device_antecedents")
            for device_id in device_antecedents:
                self.delete_antecedent(user_id, rule_id, device_id)
            device_consequents = self.r.lrange(key_pattern + ":device_consequents")
            for device_id in device_consequents:
                self.delete_consequent(user_id, rule_id, device_id)
            return "true"
        except Exception as error:
            print(repr(error))
            return "error"

    def delete_antecedent(self, user_id, rule_id, device_id):
        try:
            output = "error"
            if TIMER in device_id:
                output = self.timer_antecedent_functions.delete_antecedent(user_id, rule_id, device_id)
            elif WATER_LEVEL in device_id:
                output = self.waterlevel_antecedent_functions.delete_antecedent(user_id, rule_id, device_id)
            elif BUTTON in device_id:
                output = self.button_antecedent_functions.delete_antecedent(user_id, rule_id, device_id)
            elif SWITCH in device_id:
                output = self.switch_antecedent_functions.delete_antecedent(user_id, rule_id, device_id)
            elif WEATHER in device_id:
                output = self.weather_antecedent_functions.delete_antecedent(user_id, rule_id, device_id)
            elif PHOTOCELL in device_id:
                output = self.photocell_antecedent_functions.delete_antecedent(user_id, rule_id, device_id)
            if output != "error":
                # trigger rule evaluation
                url = self.endpoint_rabbitmq + self.publish_rule
                trigger_message = {"user_id": user_id, "rules": [rule_id]}
                requests.post(url, json.dumps(trigger_message))
                # get rule by id
                output = self.get_rule_by_id(user_id, rule_id)
            return output
        except Exception as error:
            print(repr(error))
            return "error"

    def delete_consequent(self, user_id, rule_id, device_id):
        try:
            output = "error"
            topic = ""
            payload = ""
            if ALERT in device_id:
                output = self.alert_consequent_functions.delete_consequent(user_id, rule_id, device_id)
            elif SWITCH in device_id:
                output = self.switch_consequent_functions.delete_consequent(user_id, rule_id, device_id)
                topic = self.mqtt_switch + device_id
                new_status = self.switch_consequent_functions.switch_evaluation(user_id, device_id)
                payload = new_status + "/0"
            elif SERVO in device_id:
                output = self.servo_consequent_functions.delete_consequent(user_id, rule_id, device_id)
                topic = self.mqtt_servo + device_id
                degree = self.servo_consequent_functions.servo_evaluation(user_id, device_id)
                payload = degree + "/0"
            if output != "error":
                if topic != "" and payload != "":
                    url = self.endpoint_mqtt + topic
                    message = {"message": payload}
                    requests.post(url, json.dumps(message))
                output = self.get_rule_by_id(user_id, rule_id)
            return output
        except Exception as error:
            print(repr(error))
            return "error"

    def get_rule_by_id(self, user_id, rule_id):
        try:
            key_pattern = "user:" + user_id + ":rule:" + rule_id
            rule = Rule()
            rule.id = rule_id
            rule.name = self.r.get(key_pattern + ":name")
            rule.last_time_on = self.r.get(key_pattern + ":last_time_on")
            rule.last_time_off = self.r.get(key_pattern + ":last_time_off")
            rule.last_date_on = self.r.get(key_pattern + ":last_date_on")
            rule.last_date_off = self.r.get(key_pattern + ":last_date_off")
            rule.device_antecedents = self.r.lrange(key_pattern + ":device_antecedents")
            rule.device_consequents = self.r.lrange(key_pattern + ":device_consequents")
            rule.evaluation = self.r.get(key_pattern + ":evaluation")
            rule.rule_antecedents = self.get_rule_antecedents(user_id, rule_id)
            rule.rule_consequents = self.get_rule_consequents(user_id, rule_id)
            return rule
        except Exception as error:
            print(repr(error))
            return "error"

    def get_rule_antecedents(self, user_id, rule_id):
        try:
            key_pattern = "user:" + user_id + ":rule:" + rule_id
            device_antecedents = self.r.lrange(key_pattern + ":device_antecedents")
            rule_antecedents = []
            for device_id in device_antecedents:
                antecedent = self.get_rule_antecedent_slim(user_id, rule_id, device_id)
                if antecedent != "error":
                    rule_antecedents.append(antecedent)
                else:
                    raise Exception("error retrieving antecedent")
            return rule_antecedents
        except Exception as error:
            print(repr(error))
            return "error"

    def get_rule_antecedent(self, user_id, rule_id, device_id):
        try:
            antecedent = {}
            if TIMER in device_id:
                antecedent = self.timer_antecedent_functions.get_antecedent(user_id, rule_id, device_id)
            elif WATER_LEVEL in device_id:
                antecedent = self.waterlevel_antecedent_functions.get_antecedent(user_id, rule_id, device_id)
            elif BUTTON in device_id:
                antecedent = self.button_antecedent_functions.get_antecedent(user_id, rule_id, device_id)
            elif SWITCH in device_id:
                antecedent = self.switch_antecedent_functions.get_antecedent(user_id, rule_id, device_id)
            elif WEATHER in device_id:
                antecedent = self.weather_antecedent_functions.get_antecedent(user_id, rule_id, device_id)
            elif PHOTOCELL in device_id:
                antecedent = self.photocell_antecedent_functions.get_antecedent(user_id, rule_id, device_id)
            return antecedent
        except Exception as error:
            print(repr(error))
            return "error"

    def get_rule_antecedent_slim(self, user_id, rule_id, device_id):
        try:
            antecedent = {}
            if TIMER in device_id:
                antecedent = self.timer_antecedent_functions.get_antecedent_slim(user_id, rule_id, device_id)
            elif WATER_LEVEL in device_id:
                antecedent = self.waterlevel_antecedent_functions.get_antecedent_slim(user_id, rule_id, device_id)
            elif BUTTON in device_id:
                antecedent = self.button_antecedent_functions.get_antecedent_slim(user_id, rule_id, device_id)
            elif SWITCH in device_id:
                antecedent = self.switch_antecedent_functions.get_antecedent_slim(user_id, rule_id, device_id)
            elif WEATHER in device_id:
                antecedent = self.weather_antecedent_functions.get_antecedent_slim(user_id, rule_id, device_id)
            elif PHOTOCELL in device_id:
                antecedent = self.photocell_antecedent_functions.get_antecedent_slim(user_id, rule_id, device_id)
            return antecedent
        except Exception as error:
            print(repr(error))
            return "error"

    def get_rule_consequents(self, user_id, rule_id):
        key_pattern = "user:" + user_id + ":rule:" + rule_id
        device_consequents = self.r.lrange(key_pattern + ":device_consequents")
        rule_consequents = []
        for device_id in device_consequents:
            consequent = self.get_rule_consequent_slim(user_id, rule_id, device_id)
            if consequent != "error":
                rule_consequents.append(consequent)
            else:
                raise Exception("error retrieving consequent")
        return rule_consequents

    def get_rule_consequent(self, user_id, rule_id, device_id):
        try:
            if ALERT in device_id:
                return self.alert_consequent_functions.get_consequent(user_id, rule_id, device_id)
            elif SWITCH in device_id:
                return self.switch_consequent_functions.get_consequent(user_id, rule_id, device_id)
            elif SERVO in device_id:
                return self.servo_consequent_functions.get_consequent(user_id, rule_id, device_id)
        except Exception as error:
            print(repr(error))
            return "error"

    def get_rule_consequent_slim(self, user_id, rule_id, device_id):
        try:
            if ALERT in device_id:
                return self.alert_consequent_functions.get_consequent_slim(user_id, rule_id, device_id)
            elif SWITCH in device_id:
                return self.switch_consequent_functions.get_consequent_slim(user_id, rule_id, device_id)
            elif SERVO in device_id:
                return self.servo_consequent_functions.get_consequent_slim(user_id, rule_id, device_id)
        except Exception as error:
            print(repr(error))
            return "error"

    def get_device_rules(self, user_id, device_id):
        try:
            output = list(self.r.smembers("device:" + device_id + ":rules"))
        except Exception as error:
            print(repr(error))
            return "error"
        else:
            return output
