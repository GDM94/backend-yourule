from ..components.Devices.WaterLevel.WaterLevelAntecedentFunctions import WaterLevelAntecedentFunction
from ..components.Devices.Button.ButtonAntecedentFunctions import ButtonAntecedentFunction
from ..components.Devices.Photocell.PhotocellAntecedentFunctions import PhotocellAntecedentFunction
from ..components.Devices.Weather.WeatherAntecedentFunctions import WeatherAntecedentFunction
from ..components.Rule.RuleFunctions import RuleFunction
from ..components.Devices.Alert.AlertConsequentFunctions import AlertConsequentFunction
from ..components.Devices.Switch.SwitchConsequentFunctions import SwitchConsequentFunction
from ..components.Devices.Servo.ServoConsequentFunctions import ServoConsequentFunction
from ..components.Devices.Weather.WeatherFunctions import WeatherFunction
from ..components.Devices.Timer.TimerAntecedentFunctions import TimerAntecedentFunction
from ..components.Devices.Switch.SwitchAntecedentFunctions import SwitchAntecedentFunction
from ..components.Devices.DeviceId import WATER_LEVEL, BUTTON, PHOTOCELL, SWITCH, ALERT, SERVO, WEATHER, TIMER
import json
import requests


class FunctionalRuleService(object):
    def __init__(self, redis, config):
        self.r = redis
        self.waterlevel_antecedent_functions = WaterLevelAntecedentFunction(redis)
        self.button_antecedent_functions = ButtonAntecedentFunction(redis)
        self.photocell_antecedent_functions = PhotocellAntecedentFunction(redis)
        self.weather_antecedent_function = WeatherAntecedentFunction(redis)
        self.rule_functions = RuleFunction(redis)
        self.alert_consequent_functions = AlertConsequentFunction(redis)
        self.switch_consequent_functions = SwitchConsequentFunction(redis)
        self.servo_consequent_functions = ServoConsequentFunction(redis)
        self.switch_antecedent_function = SwitchAntecedentFunction(redis)
        self.email_user = config.get("ALERT", "email_user")
        self.email_password = config.get("ALERT", "email_password")
        self.endpoint_rabbitmq = config.get("MQTT", "endpoint_rabbitmq")
        self.publish_rule = config.get("RABBITMQ", "publish_rule")
        self.api_key = config.get("OPEN_WEATHER", "api_key")
        self.api_location_url = config.get("OPEN_WEATHER", "api_location_url")
        self.api_weather_url = config.get("OPEN_WEATHER", "api_weather_url")
        self.weather_functions = WeatherFunction(redis, self.api_key, self.api_location_url, self.api_weather_url)
        self.timer_antecedent_functions = TimerAntecedentFunction(redis)

    def antecedent_evaluation(self, user_id, device_id, measure, rules):
        output = []
        for rule_id in rules:
            trigger = "false"
            if WATER_LEVEL in device_id:
                trigger = self.waterlevel_antecedent_functions. \
                    antecedent_evaluation(user_id, rule_id, device_id, measure)
            elif BUTTON in device_id:
                trigger = self.button_antecedent_functions. \
                    antecedent_evaluation(user_id, rule_id, device_id, measure)
            elif PHOTOCELL in device_id:
                trigger = self.photocell_antecedent_functions. \
                    antecedent_evaluation(user_id, rule_id, device_id, measure)
            if trigger == "true":
                output.append(rule_id)
        trigger = {"rules": output, "user_id": str(user_id)}
        return trigger

    def rule_evaluation(self, user_id, rules):
        rule_list = []
        for rule_id in rules:
            output = self.rule_functions.rule_evaluation(user_id, rule_id)
            if output == "true":
                rule_list.append(rule_id)
        trigger = {"user_id": user_id, "rules": rule_list}
        return trigger

    def consequent_evaluation(self, user_id, rule_id):
        output = []
        pattern_key = "user:" + user_id + ":rule:" + rule_id
        device_consequents = self.r.lrange(pattern_key + ":device_consequents")
        alert_id = next((s for s in device_consequents if ALERT in s), "")
        if alert_id != "":
            self.alert_consequent_functions.alert_evaluation(user_id, rule_id)
        delay = 0
        for device_id in device_consequents:
            delay = delay + int(self.r.get(pattern_key + ":rule_consequents:" + device_id + ":delay"))
            measure = "false"
            if SWITCH in device_id:
                measure = self.switch_consequent_functions.switch_evaluation(user_id, device_id)
            elif SERVO in device_id:
                measure = self.servo_consequent_functions.servo_evaluation(user_id, device_id)
            if measure != "false":
                trigger = {"device_id": device_id, "measure": measure, "delay": str(delay)}
                output.append(trigger)
        payload = {"output": output}
        return payload

    def weather_evaluation(self):
        self.update_weather()
        user_id_list = self.get_all_users()
        for user_id in user_id_list:
            device_id = WEATHER + "-" + user_id
            output = {"user_id": user_id, "rules": []}
            rule_id_list = self.get_rules_with_device_id(user_id, device_id)
            for rule_id in rule_id_list:
                trigger = self.weather_antecedent_function.evalutate_antecedent(user_id, rule_id, device_id)
                if trigger == "true":
                    output["rules"].append(rule_id)
            if len(output["rules"]) > 0:
                url = self.endpoint_rabbitmq + self.publish_rule
                requests.post(url, json.dumps(output))

    def update_weather(self):
        all_locations = list(self.r.smembers("weather:location:names"))
        for location_name in all_locations:
            self.weather_functions.update_weather(location_name)

    def get_all_users(self):
        users_keys = self.r.scan("profile:*:user_id")
        user_id_list = []
        for user_key in users_keys:
            user_id = self.r.get(user_key)
            user_id_list.append(user_id)
        return user_id_list

    def get_rules_with_device_id(self, user_id, device_id):
        rules_id_list = self.r.lrange("user:" + user_id + ":rules")
        output = []
        for rule_id in rules_id_list:
            key_pattern = "user:" + user_id + ":rule:" + rule_id
            device_antecedents = self.r.lrange(key_pattern + ":device_antecedents")
            check = next((s for s in device_antecedents if device_id in s), "")
            if check != "":
                output.append(rule_id)
        return output

    def timer_evaluation(self):
        user_id_list = self.get_all_users()
        for user_id in user_id_list:
            device_id = TIMER + "-" + user_id
            output = {"user_id": user_id, "rules": []}
            rule_id_list = self.get_rules_with_device_id(user_id, device_id)
            for rule_id in rule_id_list:
                trigger = self.timer_antecedent_functions.antecedent_evaluation(user_id, device_id, rule_id)
                if trigger == "true":
                    output["rules"].append(rule_id)
            if len(output["rules"]) > 0:
                url = self.endpoint_rabbitmq + self.publish_rule
                requests.post(url, json.dumps(output))

    def switch_last_on_evaluation(self):
        user_id_list = self.get_all_users()
        for user_id in user_id_list:
            output = {"user_id": user_id, "rules": []}
            rules_id_list = self.get_rules_with_device_id(user_id, SWITCH)
            if len(rules_id_list) > 0:
                output["rules"] = rules_id_list
                url = self.endpoint_rabbitmq + self.publish_rule
                requests.post(url, json.dumps(output))
