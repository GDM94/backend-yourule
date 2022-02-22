class WaterLevel(object):
    def __init__(self):
        self.id = ""
        self.name = "WATERLEVEL"
        self.measure = "-"
        self.absolute_measure = "-"
        self.setting_error = "0"
        self.setting_max = "100"
        self.setting_unit_measure = "cm"
        self.rules = []
        self.status = "disconnected"
        self.color = "red"
        self.unit_measure = "%"
        self.max_measure = "-"
        self.max_measure_time = "-"
        self.max_measure_date = "-"
        self.min_measure = "-"
        self.min_measure_time = "-"
        self.min_measure_date = "-"
        self.expiration = "10"
        self.type = "sensor"

    def device_mapping(self, device):
        self.id = device["id"]
        self.name = device["name"]
        self.setting_error = device["setting_error"]
        self.setting_max = device["setting_max"]
        self.setting_unit_measure = device["setting_unit_measure"]
        self.rules = device["rules"]
        self.expiration = device["expiration"]
