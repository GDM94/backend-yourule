
class Button(object):
    def __init__(self):
        self.device_id = ""
        self.name = "BUTTON"
        self.measure = "-"
        self.rules = []
        self.status = "disconnected"
        self.color = "red"
        self.unit_measure = ""
        self.last_time_on = "-"
        self.last_time_off = "-"
        self.last_date_on = "-"
        self.last_date_off = "-"
        self.expiration = "10"

    def device_mapping(self, device):
        self.device_id = device["device_id"]
        self.name = device["name"]
        self.expiration = device["expiration"]
        self.rules = device["rules"]
