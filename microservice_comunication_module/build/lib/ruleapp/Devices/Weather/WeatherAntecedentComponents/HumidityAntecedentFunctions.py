from ..WeatherAntecedentDTO import HumidityAntecedent


class HumidityAntecedentFunction(object):
    def __init__(self, redis):
        self.r = redis

    def get_humidity_antecedent(self, user_id, rule_id, device_id):
        dto = HumidityAntecedent()
        key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_antecedents:" + device_id
        dto.check_humidity = self.r.get(key_pattern + ":check_humidity")
        dto.humidity_condition = self.r.get(key_pattern + ":humidity_condition")
        dto.humidity_start_value = self.r.get(key_pattern + ":humidity_start_value")
        dto.humidity_stop_value = self.r.get(key_pattern + ":humidity_stop_value")
        dto.humidity_evaluation = self.r.get(key_pattern + ":humidity_evaluation")
        location_name = self.r.get("user:" + user_id + ":location:name")
        dto.humidity_value = self.r.get("weather:" + location_name + ":humidity")
        return dto

    def set_humidity_antecedent(self, user_id, rule_id, device_id, dto: HumidityAntecedent):
        key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_antecedents:" + device_id
        self.r.set(key_pattern + ":check_humidity", dto.check_humidity)
        self.r.set(key_pattern + ":humidity_condition", dto.humidity_condition)
        self.r.set(key_pattern + ":humidity_start_value", dto.humidity_start_value)
        self.r.set(key_pattern + ":humidity_stop_value", dto.humidity_stop_value)
        self.r.set(key_pattern + ":humidity_evaluation", dto.humidity_evaluation)

    def delete_humidity_antecedent(self, user_id, rule_id, device_id):
        key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_antecedents:" + device_id
        self.r.delete(key_pattern + ":check_humidity")
        self.r.delete(key_pattern + ":humidity_condition")
        self.r.delete(key_pattern + ":humidity_start_value")
        self.r.delete(key_pattern + ":humidity_stop_value")
        self.r.delete(key_pattern + ":humidity_evaluation")

    def register_humidity_antecedent(self, user_id, rule_id, device_id):
        key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_antecedents:" + device_id
        dto = HumidityAntecedent()
        self.r.set(key_pattern + ":check_humidity", dto.check_humidity)
        self.r.set(key_pattern + ":humidity_condition", dto.humidity_condition)
        self.r.set(key_pattern + ":humidity_start_value", dto.humidity_start_value)
        self.r.set(key_pattern + ":humidity_stop_value", dto.humidity_stop_value)
        self.r.set(key_pattern + ":humidity_evaluation", dto.humidity_evaluation)

    def humidity_antecedent_evaluation(self, user_id, rule_id, device_id):
        try:
            dto = self.get_humidity_antecedent(user_id, rule_id, device_id)
            evaluation = "true"
            if dto.check_humidity == "true":
                evaluation = "false"
                if dto.humidity_condition == "between":
                    if int(dto.humidity_start_value) < int(dto.humidity_value) <= int(dto.humidity_stop_value):
                        evaluation = "true"
                elif dto.humidity_condition == ">":
                    if int(dto.humidity_value) > int(dto.humidity_start_value):
                        evaluation = "true"
                elif dto.humidity_condition == "<":
                    if int(dto.humidity_value) < int(dto.humidity_stop_value):
                        evaluation = "true"
                if dto.humidity_evaluation != evaluation:
                    key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_antecedents:" + device_id
                    self.r.set(key_pattern + ":humidity_evaluation", evaluation)
            return evaluation
        except Exception as error:
            print(repr(error))
            return "false"
