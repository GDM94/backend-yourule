class SwitchAntecedent(object):
    def __init__(self):
        self.device_id = ""
        self.device_name = ""
        self.measure = "-"
        self.condition = "between"
        self.last_time_on = ""
        self.last_date_on = ""
        self.last_time_off = ""
        self.last_date_off = ""
        self.time_start_value = "-"
        self.date_start_value = "0"
        self.time_stop_value = "-"
        self.date_stop_value = "0"
        self.evaluation = "false"

    def antecedent_mapping(self, antecedent):
        self.device_id = antecedent["device_id"]
        self.device_name = antecedent["device_name"]
        self.time_start_value = antecedent["time_start_value"]
        self.date_start_value = antecedent["date_start_value"]
        self.time_stop_value = antecedent["time_stop_value"]
        self.date_stop_value = antecedent["date_stop_value"]
