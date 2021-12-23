import json
from ruleapp.Devices.Weather.WeatherFunctions import WeatherFunction
from ruleapp.Devices.Weather.WeatherAntecedentFunctions import WeatherAntecedentFunction
from ruleapp.Devices.DeviceId import WEATHER


class WeatherServiceEvaluation(object):
    def __init__(self, rabbitmq, redis, config):
        self.r = redis
        self.rabbitmq = rabbitmq
        self.weather_antecedent_function = WeatherAntecedentFunction(redis)
        self.api_key = config.get("OPEN_WEATHER", "api_key")
        self.api_location_url = config.get("OPEN_WEATHER", "api_location_url")
        self.api_weather_url = config.get("OPEN_WEATHER", "api_weather_url")
        self.weather_functions = WeatherFunction(redis, self.api_key, self.api_location_url, self.api_weather_url)

    def get_all_users(self):
        users_keys = self.r.scan("profile:*:user_id")
        user_id_list = []
        for user_key in users_keys:
            user_id = self.r.get(user_key)
            user_id_list.append(user_id)
        return user_id_list

    def get_rules_with_weather(self, user_id, device_id):
        rules_id_list = self.r.lrange("user:" + user_id + ":rules")
        output = []
        for rule_id in rules_id_list:
            key_pattern = "user:" + user_id + ":rule:" + rule_id
            device_antecedents = self.r.lrange(key_pattern + ":device_antecedents")
            if device_id in device_antecedents:
                output.append(rule_id)
        return output

    def weather_trigger(self):
        self.update_weather()
        user_id_list = self.get_all_users()
        for user_id in user_id_list:
            device_id = WEATHER + "-" + user_id
            output = {"user_id": user_id, "rules": []}
            rule_id_list = self.get_rules_with_weather(user_id, device_id)
            for rule_id in rule_id_list:
                trigger = self.weather_antecedent_function.evalutate_antecedent(user_id, rule_id, device_id)
                if trigger == "true":
                    output["rules"].append(rule_id)
            if len(output["rules"]) > 0:
                payload = json.dumps(output)
                self.rabbitmq.publish(payload)

    def update_weather(self):
        all_locations = list(self.r.smembers("weather:location:names"))
        for location_name in all_locations:
            self.weather_functions.update_weather(location_name)
