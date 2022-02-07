from ..components.Devices.DeviceId import WATER_LEVEL, BUTTON, PHOTOCELL, SWITCH, SERVO, WEATHER, TIMER
from flask import current_app as app


class AntecedentEvaluationService(object):
    def __init__(self, redis):
        self.r = redis

    def antecedent_evaluation(self, user_id, device_id, measure, rules):
        output = []
        for rule_id in rules:
            trigger = "false"
            if WATER_LEVEL in device_id:
                trigger = app.waterlevel_antecedent_functions. \
                    antecedent_evaluation(user_id, rule_id, device_id, measure)
            elif BUTTON in device_id:
                trigger = app.button_antecedent_functions. \
                    antecedent_evaluation(user_id, rule_id, device_id, measure)
            elif PHOTOCELL in device_id:
                trigger = app.photocell_antecedent_functions. \
                    antecedent_evaluation(user_id, rule_id, device_id, measure)
            elif SWITCH in device_id:
                trigger = app.switch_antecedent_functions.antecedent_evaluation(user_id, device_id, measure, rule_id)
            elif SERVO in device_id:
                trigger = app.servo_antecedent_functions.antecedent_evaluation(user_id, device_id, measure, rule_id)
            elif TIMER in device_id:
                trigger = app.timer_antecedent_functions.antecedent_evaluation(user_id, device_id, rule_id)
            elif WEATHER in device_id:
                trigger = app.weather_antecedent_function.evalutate_antecedent(user_id, rule_id, device_id)
            if trigger == "true":
                output.append(rule_id)
        if len(output) > 0:
            app.rule_evaluation_service.rules_evaluation(user_id, rules)

    def weather_evaluation(self):
        all_locations = list(self.r.smembers("weather:location:names"))
        for location_name in all_locations:
            app.weather_functions.update_weather(location_name)
        user_id_list = self.get_all_users()
        for user_id in user_id_list:
            device_id = WEATHER + "-" + user_id
            rule_id_list = self.get_rules_with_device_id(user_id, device_id)
            self.antecedent_evaluation(user_id, device_id, "", rule_id_list)

    def timer_evaluation(self):
        user_id_list = self.get_all_users()
        for user_id in user_id_list:
            device_id = TIMER + "-" + user_id
            rule_id_list = self.get_rules_with_device_id(user_id, device_id)
            self.antecedent_evaluation(user_id, device_id, "", rule_id_list)

    def switch_last_on_evaluation(self):
        user_id_list = self.get_all_users()
        for user_id in user_id_list:
            rules_id_list = self.get_rules_with_device_id(user_id, SWITCH)
            for rule_id in rules_id_list:
                key_pattern = "user:" + user_id + ":rule:" + rule_id
                device_antecedents = self.r.lrange(key_pattern + ":device_antecedents")
                for device_id in device_antecedents:
                    if SWITCH in device_id and self.r.exists("device:" + device_id + ":measure") == 1:
                        measure = self.r.get("device:" + device_id + ":measure")
                        self.antecedent_evaluation(user_id, device_id, measure, rules_id_list)

    def servo_last_on_evaluation(self):
        user_id_list = self.get_all_users()
        for user_id in user_id_list:
            rules_id_list = self.get_rules_with_device_id(user_id, SERVO)
            for rule_id in rules_id_list:
                key_pattern = "user:" + user_id + ":rule:" + rule_id
                device_antecedents = self.r.lrange(key_pattern + ":device_antecedents")
                for device_id in device_antecedents:
                    if SERVO in device_id and self.r.exists("device:" + device_id + ":measure") == 1:
                        measure = self.r.get("device:" + device_id + ":measure")
                        self.antecedent_evaluation(user_id, device_id, measure, rules_id_list)

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
