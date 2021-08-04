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
        self.order = ""
        self.check_time = "true"
        self.check_date = "true"
