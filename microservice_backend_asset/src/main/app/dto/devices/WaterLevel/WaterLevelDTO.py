class WaterLevel(object):
    def __init__(self):
        self.device_id = ""
        self.name = "WATERLEVEL"
        self.measure = "-"
        self.absolute_measure = "-"
        self.setting_error = "0"
        self.setting_max = "100"
        self.setting_unit_measure = "cm"
        self.expiration = "10"
        self.rules = []
        self.status = "initialization"
        self.color = "yellow"
        self.unit_measure = "%"
        self.max_measure = "-"
        self.max_measure_time = "-"
        self.min_measure = "-"
        self.min_measure_time = "-"
