from ..WeatherAntecedentDTO import IconAntecedent


class IconAntecedentFunction(object):
    def __init__(self, redis):
        self.r = redis
        self.icon_codes = {
            "01d": 1,  # clear sky
            "02d": 2,  # few clouds
            "03d": 3,  # scattered clouds
            "04d": 4,  # broken clouds
            "09d": 5,  # shower rain
            "10d": 6,  # rain
            "11d": 7,  # thunderstorm
            "13d": 8,  # snow
            "50d": 9  # mist
        }

    def get_icon_antecedent(self, user_id, rule_id, device_id):
        dto = IconAntecedent()
        key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_antecedents:" + device_id
        dto.check_icon = self.r.get(key_pattern + ":check_icon")
        dto.icon_condition = self.r.get(key_pattern + ":icon_condition")
        dto.icon_start_value = list(self.r.smembers(key_pattern + ":icon_start_value"))
        dto.icon_evaluation = self.r.get(key_pattern + ":icon_evaluation")
        location_name = self.r.get("user:" + user_id + ":location:name")
        dto.icon_value = list(self.r.smembers("weather:" + location_name + ":icon"))
        return dto

    def set_icon_antecedent(self, user_id, rule_id, device_id, dto: IconAntecedent):
        key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_antecedents:" + device_id
        self.r.set(key_pattern + ":check_icon", dto.check_icon)
        self.r.set(key_pattern + ":icon_condition", dto.icon_condition)
        self.r.delete(key_pattern + ":icon_start_value")
        if len(dto.icon_start_value) > 0:
            for icon in dto.icon_start_value:
                self.r.sadd(key_pattern + ":icon_start_value", icon)
        self.r.set(key_pattern + ":icon_evaluation", dto.icon_evaluation)

    def delete_icon_antecedent(self, user_id, rule_id, device_id):
        key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_antecedents:" + device_id
        self.r.delete(key_pattern + ":check_icon")
        self.r.delete(key_pattern + ":icon_condition")
        self.r.delete(key_pattern + ":icon_start_value")
        self.r.delete(key_pattern + ":icon_evaluation")

    def register_icon_antecedent(self, user_id, rule_id, device_id):
        dto = IconAntecedent()
        key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_antecedents:" + device_id
        self.r.set(key_pattern + ":check_icon", dto.check_icon)
        self.r.set(key_pattern + ":icon_condition", dto.icon_condition)
        self.r.set(key_pattern + ":icon_evaluation", dto.icon_evaluation)

    def icon_antecedent_evaluation(self, user_id, rule_id, device_id):
        try:
            dto = self.get_icon_antecedent(user_id, rule_id, device_id)
            evaluation = "true"
            if dto.check_icon == "true":
                evaluation = "false"
                check = set.intersection(set(dto.icon_value), set(dto.icon_start_value))
                if len(check) > 0:
                    evaluation = "true"
                if dto.icon_evaluation != evaluation:
                    key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_antecedents:" + device_id
                    self.r.set(key_pattern + ":icon_evaluation", evaluation)
            return evaluation
        except Exception as error:
            print(repr(error))
            return "false"
