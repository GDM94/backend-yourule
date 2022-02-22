class Timer(object):
    def __init__(self):
        self.id = ""
        self.name = "timer"
        self.measure_time = ""
        self.measure_day = ""
        self.measure = ""
        self.rules = []
        self.status = "connected"
        self.color = "green"
        self.expiration = "no"
        self.type = "sensor"

    def device_mapping(self, device):
        self.id = device["id"]
        self.name = device["name"]
        self.rules = device["rules"]
