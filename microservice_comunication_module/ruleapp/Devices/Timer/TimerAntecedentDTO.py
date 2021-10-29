
class TimerAntecedent(object):
    def __init__(self):
        self.device_id = ""
        self.device_name = ""
        self.measure_time = ""
        self.measure_day = ""
        self.condition_time = "between"
        self.condition_day = "="
        self.day_start_value = []
        self.time_start_value = ""
        self.time_stop_value = ""
        self.evaluation = "false"
        self.check_time = "true"
        self.check_date = "true"

    def antecedent_mapping(self, antecedent):
        self.device_id = antecedent["device_id"]
        self.device_name = antecedent["device_name"]
        self.condition_time = antecedent["condition_time"]
        self.condition_day = antecedent["condition_day"]
        self.check_time = antecedent["check_time"]
        self.check_date = antecedent["check_date"]
        self.day_start_value = antecedent["day_start_value"]
        self.time_start_value = antecedent["time_start_value"]
        self.time_stop_value = antecedent["time_stop_value"]
