from .WeatherAntecedentComponents.CloudAntecedentFunctions import CloudAntecedentFunction
from .WeatherAntecedentComponents.HumidityAntecedentFunctions import HumidityAntecedentFunction
from .WeatherAntecedentComponents.IconAntecedentFunctions import IconAntecedentFunction
from .WeatherAntecedentComponents.PressureAntecedentFunctions import PressureAntecedentFunction
from .WeatherAntecedentComponents.TempAntecedentFunctions import TempAntecedentFunction
from .WeatherAntecedentComponents.TimeAntecedentFunctions import TimeAntecedentFunction
from .WeatherAntecedentComponents.WindSpeedAntecedentFunctions import WindSpeedAntecedentFunction
from .WeatherAntecedentDTO import WeatherAntecedent


class WeatherAntecedentFunction(object):
    def __init__(self, redis):
        self.r = redis
        self.icon_antecedent_functions = IconAntecedentFunction(redis)
        self.temp_antecedent_functions = TempAntecedentFunction(redis)
        self.pressure_antecedent_functions = PressureAntecedentFunction(redis)
        self.humidity_antecedent_functions = HumidityAntecedentFunction(redis)
        self.cloud_antecedent_functions = CloudAntecedentFunction(redis)
        self.time_antecedent_functions = TimeAntecedentFunction(redis)
        self.wind_speed_antecedent_functions = WindSpeedAntecedentFunction(redis)

    def get_antecedent(self, user_id, rule_id, device_id):
        try:
            antecedent = WeatherAntecedent()
            antecedent.device_id = device_id
            antecedent.device_name = self.r.get("device:" + device_id + ":name")
            key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_antecedents:" + device_id
            antecedent.evaluation = self.r.get(key_pattern + ":evaluation")
            antecedent.set_icon_antecedent(
                self.icon_antecedent_functions.get_icon_antecedent(user_id, rule_id, device_id))
            antecedent.set_temp_antecedent(
                self.temp_antecedent_functions.get_temp_antecedent(user_id, rule_id, device_id))
            antecedent.set_pressure_antecedent(
                self.pressure_antecedent_functions.get_pressure_antecedent(user_id, rule_id, device_id))
            antecedent.set_cloud_antecedent(
                self.cloud_antecedent_functions.get_cloud_antecedent(user_id, rule_id, device_id))
            antecedent.set_humidity_antecedent(
                self.humidity_antecedent_functions.get_humidity_antecedent(user_id, rule_id, device_id))
            antecedent.set_time_antecedent(
                self.time_antecedent_functions.get_time_antecedent(user_id, rule_id, device_id))
            antecedent.set_wind_antecedent(
                self.wind_speed_antecedent_functions.get_wind_antecedent(user_id, rule_id, device_id))
            return antecedent
        except Exception as error:
            print(repr(error))
            return "error"

    def get_antecedent_slim(self, user_id, rule_id, device_id):
        try:
            antecedent = WeatherAntecedent()
            antecedent.device_id = device_id
            antecedent.device_name = self.r.get("device:" + device_id + ":name")
            key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_antecedents:" + device_id
            antecedent.evaluation = self.r.get(key_pattern + ":evaluation")
            return antecedent
        except Exception as error:
            print(repr(error))
            return "error"

    def update_antecedent(self, user_id, rule_id, new_antecedent):
        try:
            antecedent = WeatherAntecedent()
            antecedent.antecedent_mapping(new_antecedent)
            self.icon_antecedent_functions.set_icon_antecedent(user_id, rule_id, antecedent.device_id,
                                                               antecedent.get_icon_antecedent())
            self.cloud_antecedent_functions.set_cloud_antecedent(user_id, rule_id, antecedent.device_id,
                                                                 antecedent.get_cloud_antecedent())
            self.humidity_antecedent_functions.set_humidity_antecedent(user_id, rule_id, antecedent.device_id,
                                                                       antecedent.get_humidity_antecedent())
            self.pressure_antecedent_functions.set_pressure_antecedent(user_id, rule_id, antecedent.device_id,
                                                                       antecedent.get_pressure_antecedent())
            self.temp_antecedent_functions.set_temp_antecedent(user_id, rule_id, antecedent.device_id,
                                                               antecedent.get_temp_antecedent())
            self.time_antecedent_functions.set_time_antecedent(user_id, rule_id, antecedent.device_id,
                                                               antecedent.get_time_antecedent())
            self.wind_speed_antecedent_functions.set_wind_antecedent(user_id, rule_id, antecedent.device_id,
                                                                     antecedent.get_wind_antecedent())
            return "true"
        except Exception as error:
            print(repr(error))
            return "error"

    def delete_antecedent(self, user_id, rule_id, device_id):
        try:
            self.cloud_antecedent_functions.delete_cloud_antecedent(user_id, rule_id, device_id)
            self.humidity_antecedent_functions.delete_humidity_antecedent(user_id, rule_id, device_id)
            self.icon_antecedent_functions.delete_icon_antecedent(user_id, rule_id, device_id)
            self.pressure_antecedent_functions.delete_pressure_antecedent(user_id, rule_id, device_id)
            self.temp_antecedent_functions.delete_temp_antecedent(user_id, rule_id, device_id)
            self.time_antecedent_functions.delete_time_antecedent(user_id, rule_id, device_id)
            self.wind_speed_antecedent_functions.delete_wind_antecedent(user_id, rule_id, device_id)
            key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_antecedents:" + device_id
            self.r.delete(key_pattern + ":evaluation")
            self.r.lrem("device:" + device_id + ":rules", rule_id)
            self.r.lrem("user:" + user_id + ":rule:" + rule_id + ":device_antecedents", device_id)
            return "true"
        except Exception as error:
            print(repr(error))
            return "error"

    def add_antecedent(self, user_id, rule_id, device_id):
        try:
            device_antecedents = self.r.lrange("user:" + user_id + ":rule:" + rule_id + ":device_antecedents")
            result = "false"
            if device_id not in device_antecedents:
                self.r.rpush("device:" + device_id + ":rules", rule_id)
                self.r.rpush("user:" + user_id + ":rule:" + rule_id + ":device_antecedents", device_id)
                key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_antecedents:" + device_id
                self.r.set(key_pattern + ":evaluation", "false")
                self.cloud_antecedent_functions.register_cloud_antecedent(user_id, rule_id, device_id)
                self.humidity_antecedent_functions.register_humidity_antecedent(user_id, rule_id, device_id)
                self.icon_antecedent_functions.register_icon_antecedent(user_id, rule_id, device_id)
                self.pressure_antecedent_functions.register_pressure_antecedent(user_id, rule_id, device_id)
                self.temp_antecedent_functions.register_temp_antecedent(user_id, rule_id, device_id)
                self.time_antecedent_functions.register_time_antecedent(user_id, rule_id, device_id)
                self.wind_speed_antecedent_functions.register_wind_speed_antecedent(user_id, rule_id, device_id)
                result = "true"
            return result
        except Exception as error:
            print(repr(error))
            return "error"

    def evalutate_antecedent(self, user_id, rule_id, device_id):
        try:
            key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_antecedents:" + device_id
            old_evaluation = self.r.get(key_pattern + ":evaluation")
            evaluations = []
            cloud_evaluation = self.cloud_antecedent_functions.clouds_antecedent_evaluation(user_id, rule_id, device_id)
            humidity_evaluation = self.humidity_antecedent_functions.humidity_antecedent_evaluation(user_id, rule_id,
                                                                                                    device_id)
            icon_evaluation = self.icon_antecedent_functions.icon_antecedent_evaluation(user_id, rule_id, device_id)
            pressure_evaluation = self.pressure_antecedent_functions.pressure_antecedent_evaluation(user_id, rule_id,
                                                                                                    device_id)
            temp_evaluation = self.temp_antecedent_functions.temp_antecedent_evaluation(user_id, rule_id, device_id)
            time_evaluation = self.time_antecedent_functions.time_antecedent_evaluation(user_id, rule_id, device_id)
            wind_speed_evaluation = self.wind_speed_antecedent_functions.wind_antecedent_evaluation(user_id, rule_id,
                                                                                                    device_id)
            evaluations.append(cloud_evaluation)
            evaluations.append(humidity_evaluation)
            evaluations.append(icon_evaluation)
            evaluations.append(pressure_evaluation)
            evaluations.append(temp_evaluation)
            evaluations.append(time_evaluation)
            evaluations.append(wind_speed_evaluation)
            evaluation = "true"
            if "false" in evaluations:
                evaluation = "false"
            trigger = "false"
            if old_evaluation != evaluation:
                trigger = "true"
                key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_antecedents:" + device_id
                self.r.set(key_pattern + ":evaluation", evaluation)
            return trigger
        except Exception as error:
            print(repr(error))
            return "false"
