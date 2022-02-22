class Photocell(object):
    def __init__(self):
        self.id = ""
        self.name = "PHOTOCELL"
        self.measure = "-"
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
        self.rules = device["rules"]
        self.expiration = device["expiration"]