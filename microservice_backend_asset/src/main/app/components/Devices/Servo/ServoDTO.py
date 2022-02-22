class Servo(object):
    def __init__(self):
        self.id = ""
        self.name = "servo"
        self.measure = "-"
        self.absolute_measure = "90"
        self.rules = []
        self.automatic = "true"
        self.manual_measure = "off"
        self.setting_on = "0"
        self.setting_off = "90"
        self.setting_unit_measure = "degree"
        self.last_date_on = "-"
        self.last_date_off = "-"
        self.last_time_on = "-"
        self.last_time_off = "-"
        self.status = "disconnected"
        self.color = "red"
        self.expiration = "10"
        self.type = "actuator"

    def device_mapping(self, device):
        self.id = device["id"]
        self.name = device["name"]
        self.rules = device["rules"]
        self.automatic = device["automatic"]
        self.manual_measure = device["manual_measure"]
        self.setting_on = device["setting_on"]
        self.setting_off = device["setting_off"]
        self.expiration = device["expiration"]
