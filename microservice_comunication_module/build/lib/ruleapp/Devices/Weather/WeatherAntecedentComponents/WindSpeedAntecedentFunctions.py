from ..WeatherAntecedentDTO import WindAntecedent


class WindSpeedAntecedentFunction(object):
    def __init__(self, redis):
        self.r = redis

    def get_wind_antecedent(self, user_id, rule_id, device_id):
        dto = WindAntecedent()
        key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_antecedents:" + device_id
        dto.check_wind_speed = self.r.get(key_pattern + ":check_wind_speed")
        dto.wind_speed_condition = self.r.get(key_pattern + ":wind_speed_condition")
        dto.wind_speed_start_value = self.r.get(key_pattern + ":wind_speed_start_value")
        dto.wind_speed_stop_value = self.r.get(key_pattern + ":wind_speed_stop_value")
        dto.wind_speed_evaluation = self.r.get(key_pattern + ":wind_speed_evaluation")
        location_name = self.r.get("user:" + user_id + ":location:name")
        dto.wind_speed_value = self.r.get("weather:" + location_name + ":wind_speed")
        return dto

    def set_wind_antecedent(self, user_id, rule_id, device_id, dto: WindAntecedent):
        key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_antecedents:" + device_id
        self.r.set(key_pattern + ":check_wind_speed", dto.check_wind_speed)
        self.r.set(key_pattern + ":wind_speed_condition", dto.wind_speed_condition)
        self.r.set(key_pattern + ":wind_speed_start_value", dto.wind_speed_start_value)
        self.r.set(key_pattern + ":wind_speed_stop_value", dto.wind_speed_stop_value)
        self.r.set(key_pattern + ":wind_speed_evaluation", dto.wind_speed_evaluation)

    def delete_wind_antecedent(self, user_id, rule_id, device_id):
        key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_antecedents:" + device_id
        self.r.delete(key_pattern + ":check_wind_speed")
        self.r.delete(key_pattern + ":wind_speed_condition")
        self.r.delete(key_pattern + ":wind_speed_start_value")
        self.r.delete(key_pattern + ":wind_speed_stop_value")
        self.r.delete(key_pattern + ":wind_speed_evaluation")

    def register_wind_speed_antecedent(self, user_id, rule_id, device_id):
        dto = WindAntecedent()
        key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_antecedents:" + device_id
        self.r.set(key_pattern + ":check_wind_speed", dto.check_wind_speed)
        self.r.set(key_pattern + ":wind_speed_condition", dto.wind_speed_condition)
        self.r.set(key_pattern + ":wind_speed_start_value", dto.wind_speed_start_value)
        self.r.set(key_pattern + ":wind_speed_stop_value", dto.wind_speed_stop_value)
        self.r.set(key_pattern + ":wind_speed_evaluation", dto.wind_speed_evaluation)

    def wind_antecedent_evaluation(self, user_id, rule_id, device_id):
        try:
            dto = self.get_wind_antecedent(user_id, rule_id, device_id)
            evaluation = "true"
            if dto.check_wind_speed == "true":
                evaluation = "false"
                if dto.wind_speed_condition == "between":
                    if float(dto.wind_speed_start_value) < float(dto.wind_speed_value) <= float(dto.wind_speed_stop_value):
                        evaluation = "true"
                elif dto.wind_speed_condition == ">":
                    if float(dto.wind_speed_value) > float(dto.wind_speed_start_value):
                        evaluation = "true"
                elif dto.wind_speed_condition == "<":
                    if float(dto.wind_speed_value) < float(dto.wind_speed_stop_value):
                        evaluation = "true"
                if dto.wind_speed_evaluation != evaluation:
                    key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_antecedents:" + device_id
                    self.r.set(key_pattern + ":wind_speed_evaluation", evaluation)
            return evaluation
        except Exception as error:
            print(repr(error))
            return "false"
