from ..WeatherAntecedentDTO import TempAntecedent


class TempAntecedentFunction(object):
    def __init__(self, redis):
        self.r = redis

    def get_temp_antecedent(self, user_id, rule_id, device_id):
        dto = TempAntecedent()
        key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_antecedents:" + device_id
        dto.check_temp = self.r.get(key_pattern + ":check_temp")
        dto.temp_condition = self.r.get(key_pattern + ":temp_condition")
        dto.temp_start_value = self.r.get(key_pattern + ":temp_start_value")
        dto.temp_stop_value = self.r.get(key_pattern + ":temp_stop_value")
        dto.temp_evaluation = self.r.get(key_pattern + ":temp_evaluation")
        location_name = self.r.get("user:" + user_id + ":location:name")
        dto.temp_value = self.r.get("weather:" + location_name + ":temp")
        return dto

    def set_temp_antecedent(self, user_id, rule_id, device_id, dto: TempAntecedent):
        key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_antecedents:" + device_id
        self.r.set(key_pattern + ":check_temp", dto.check_temp)
        self.r.set(key_pattern + ":temp_condition", dto.temp_condition)
        self.r.set(key_pattern + ":temp_start_value", dto.temp_start_value)
        self.r.set(key_pattern + ":temp_stop_value", dto.temp_stop_value)
        self.r.set(key_pattern + ":temp_evaluation", dto.temp_evaluation)

    def delete_temp_antecedent(self, user_id, rule_id, device_id):
        key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_antecedents:" + device_id
        self.r.delete(key_pattern + ":check_temp")
        self.r.delete(key_pattern + ":temp_condition")
        self.r.delete(key_pattern + ":temp_start_value")
        self.r.delete(key_pattern + ":temp_stop_value")
        self.r.delete(key_pattern + ":temp_evaluation")

    def register_temp_antecedent(self, user_id, rule_id, device_id):
        dto = TempAntecedent()
        key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_antecedents:" + device_id
        self.r.set(key_pattern + ":check_temp", dto.check_temp)
        self.r.set(key_pattern + ":temp_condition", dto.temp_condition)
        self.r.set(key_pattern + ":temp_start_value", dto.temp_start_value)
        self.r.set(key_pattern + ":temp_stop_value", dto.temp_stop_value)
        self.r.set(key_pattern + ":temp_evaluation", dto.temp_evaluation)

    def temp_antecedent_evaluation(self, user_id, rule_id, device_id):
        try:
            dto = self.get_temp_antecedent(user_id, rule_id, device_id)
            evaluation = "true"
            if dto.check_temp == "true":
                evaluation = "false"
                if dto.temp_condition == "between":
                    if float(dto.temp_start_value) < float(dto.temp_value) <= float(dto.temp_stop_value):
                        evaluation = "true"
                elif dto.temp_condition == ">":
                    if float(dto.temp_value) > float(dto.temp_start_value):
                        evaluation = "true"
                elif dto.temp_condition == "<":
                    if float(dto.temp_value) < float(dto.temp_stop_value):
                        evaluation = "true"
                if dto.temp_evaluation != evaluation:
                    key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_antecedents:" + device_id
                    self.r.set(key_pattern + ":temp_evaluation", evaluation)
            return evaluation
        except Exception as error:
            print(repr(error))
            return "false"
