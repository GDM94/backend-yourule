
class Button(object):
    def __init__(self):
        self.id = ""
        self.name = "BUTTON"
        self.measure = "-"
        self.rules = []
        self.status = "disconnected"
        self.color = "red"
        self.last_time_on = "-"
        self.last_time_off = "-"
        self.last_date_on = "-"
        self.last_date_off = "-"
        self.expiration = "10"

    def device_mapping(self, device):
        self.id = device["id"]
        self.name = device["name"]
        self.rules = device["rules"]
        self.expiration = device["expiration"]
