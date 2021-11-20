from ..WeatherAntecedentDTO import PressureAntecedent


class PressureAntecedentFunction(object):
    def __init__(self, redis):
        self.r = redis

    def get_pressure_antecedent(self, user_id, rule_id, device_id):
        dto = PressureAntecedent()
        key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_antecedents:" + device_id
        dto.check_pressure = self.r.get(key_pattern + ":check_pressure")
        dto.pressure_condition = self.r.get(key_pattern + ":pressure_condition")
        dto.pressure_start_value = self.r.get(key_pattern + ":pressure_start_value")
        dto.pressure_stop_value = self.r.get(key_pattern + ":pressure_stop_value")
        dto.pressure_evaluation = self.r.get(key_pattern + ":pressure_evaluation")
        location_name = self.r.get("user:" + user_id + ":location:name")
        dto.pressure_value = self.r.get("weather:" + location_name + ":pressure")
        return dto

    def set_pressure_antecedent(self, user_id, rule_id, device_id, dto: PressureAntecedent):
        key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_antecedents:" + device_id
        self.r.set(key_pattern + ":check_pressure", dto.check_pressure)
        self.r.set(key_pattern + ":pressure_condition", dto.pressure_condition)
        self.r.set(key_pattern + ":pressure_start_value", dto.pressure_start_value)
        self.r.set(key_pattern + ":pressure_stop_value", dto.pressure_stop_value)
        self.r.set(key_pattern + ":pressure_evaluation", dto.pressure_evaluation)

    def delete_pressure_antecedent(self, user_id, rule_id, device_id):
        key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_antecedents:" + device_id
        self.r.delete(key_pattern + ":check_pressure")
        self.r.delete(key_pattern + ":pressure_condition")
        self.r.delete(key_pattern + ":pressure_start_value")
        self.r.delete(key_pattern + ":pressure_stop_value")
        self.r.delete(key_pattern + ":pressure_evaluation")

    def register_pressure_antecedent(self, user_id, rule_id, device_id):
        dto = PressureAntecedent()
        key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_antecedents:" + device_id
        self.r.set(key_pattern + ":check_pressure", dto.check_pressure)
        self.r.set(key_pattern + ":pressure_condition", dto.pressure_condition)
        self.r.set(key_pattern + ":pressure_start_value", dto.pressure_start_value)
        self.r.set(key_pattern + ":pressure_stop_value", dto.pressure_stop_value)
        self.r.set(key_pattern + ":pressure_evaluation", dto.pressure_evaluation)

    def pressure_antecedent_evaluation(self, user_id, rule_id, device_id):
        try:
            dto = self.get_pressure_antecedent(user_id, rule_id, device_id)
            evaluation = "true"
            if dto.check_pressure == "true":
                evaluation = "false"
                if dto.pressure_condition == "between":
                    if dto.pressure_start_value < dto.pressure_value <= dto.pressure_stop_value:
                        evaluation = "true"
                elif dto.pressure_condition == ">":
                    if dto.pressure_value > dto.pressure_start_value:
                        evaluation = "true"
                elif dto.pressure_condition == "<":
                    if dto.pressure_value < dto.pressure_stop_value:
                        evaluation = "true"
                if dto.pressure_evaluation != evaluation:
                    key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_antecedents:" + device_id
                    self.r.set(key_pattern + ":pressure_evaluation", evaluation)
            return evaluation
        except Exception as error:
            print(repr(error))
            return "false"
