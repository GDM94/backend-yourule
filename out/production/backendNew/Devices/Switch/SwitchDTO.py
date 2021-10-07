
class Switch(object):
    def __init__(self):
        self.device_id = ""
        self.name = "switch"
        self.measure = "-"
        self.rules = []
        self.automatic = "true"
        self.manual_measure = "false"
        self.last_date_on = "-"
        self.last_date_off = "-"
        self.last_time_on = "-"
        self.last_time_off = "-"
        self.status = "disconnected"
        self.color = "red"
        self.expire_time = "10"

    def device_mapping(self, device):
        self.device_id = device["device_id"]
        self.name = device["name"]
        self.rules = device["rules"]
        self.automatic = device["automatic"]
        self.manual_measure = device["manual_measure"]
