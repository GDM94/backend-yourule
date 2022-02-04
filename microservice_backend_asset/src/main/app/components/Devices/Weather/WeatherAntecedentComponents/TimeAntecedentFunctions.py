from ..WeatherAntecedentDTO import TimeAntecedent
from datetime import datetime


class TimeAntecedentFunction(object):
    def __init__(self, redis):
        self.r = redis

    def get_time_antecedent(self, user_id, rule_id, device_id):
        dto = TimeAntecedent()
        key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_antecedents:" + device_id
        dto.check_time = self.r.get(key_pattern + ":check_time")
        dto.time_condition = self.r.get(key_pattern + ":time_condition")
        dto.time_start_value = self.r.get(key_pattern + ":time_start_value")
        dto.time_stop_value = self.r.get(key_pattern + ":time_stop_value")
        dto.time_evaluation = self.r.get(key_pattern + ":time_evaluation")
        location_name = self.r.get("user:" + user_id + ":location:name")
        dto.sunrise = self.r.get("weather:" + location_name + ":sunrise")
        dto.sunset = self.r.get("weather:" + location_name + ":sunset")
        dto.time_value = datetime.now().strftime("%H:%M")
        return dto

    def set_time_antecedent(self, user_id, rule_id, device_id, dto: TimeAntecedent):
        key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_antecedents:" + device_id
        self.r.set(key_pattern + ":check_time", dto.check_time)
        self.r.set(key_pattern + ":time_condition", dto.time_condition)
        self.r.set(key_pattern + ":time_start_value", dto.time_start_value)
        self.r.set(key_pattern + ":time_stop_value", dto.time_stop_value)
        self.r.set(key_pattern + ":time_evaluation", dto.time_evaluation)

    def delete_time_antecedent(self, user_id, rule_id, device_id):
        key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_antecedents:" + device_id
        self.r.delete(key_pattern + ":check_time")
        self.r.delete(key_pattern + ":time_condition")
        self.r.delete(key_pattern + ":time_start_value")
        self.r.delete(key_pattern + ":time_stop_value")
        self.r.delete(key_pattern + ":time_evaluation")

    def register_time_antecedent(self, user_id, rule_id, device_id):
        dto = TimeAntecedent()
        key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_antecedents:" + device_id
        self.r.set(key_pattern + ":check_time", dto.check_time)
        self.r.set(key_pattern + ":time_condition", dto.time_condition)
        self.r.set(key_pattern + ":time_start_value", dto.time_start_value)
        self.r.set(key_pattern + ":time_stop_value", dto.time_stop_value)
        self.r.set(key_pattern + ":time_evaluation", dto.time_evaluation)

    def time_antecedent_evaluation(self, user_id, rule_id, device_id):
        try:
            dto = self.get_time_antecedent(user_id, rule_id, device_id)
            evaluation = "true"
            if dto.check_time == "true":
                evaluation = "false"
                time_start_value = datetime.strptime(dto.time_start_value, '%H:%M').time()
                time_value = datetime.strptime(dto.time_value, '%H:%M').time()
                time_stop_value = datetime.strptime(dto.time_stop_value, '%H:%M').time()
                if time_start_value < time_value <= time_stop_value:
                    evaluation = "true"
                if dto.time_evaluation != evaluation:
                    key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_antecedents:" + device_id
                    self.r.set(key_pattern + ":time_evaluation", evaluation)
            return evaluation
        except Exception as error:
            print(repr(error))
            return "false"
