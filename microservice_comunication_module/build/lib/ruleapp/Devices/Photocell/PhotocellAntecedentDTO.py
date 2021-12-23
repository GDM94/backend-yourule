class PhotocellAntecedent(object):
    def __init__(self):
        self.device_id = ""
        self.device_name = ""
        self.measure = "-"
        self.condition_measure = "between"
        self.start_value = "//"
        self.stop_value = "//"
        self.last_time_on = "-"
        self.last_time_off = "-"
        self.last_date_on = "-"
        self.last_date_off = "-"
        self.evaluation = "false"

    def antecedent_mapping(self, antecedent):
        self.device_id = antecedent["device_id"]
        self.device_name = antecedent["device_name"]
        self.condition_measure = antecedent["condition_measure"]
        self.start_value = antecedent["start_value"]
        self.stop_value = antecedent["stop_value"]
