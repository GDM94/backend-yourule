
class AlertConsequent(object):
    def __init__(self):
        self.device_id = ""
        self.device_name = ""
        self.message = ""
        self.if_value = "on"
        self.else_value = "off"
        self.delay = "0"
        self.delay_unit_measure = "seconds"
        self.order = ""

    def consequent_mapping(self, consequent):
        self.device_id = consequent["device_id"]
        self.device_name = consequent["device_name"]
        self.message = consequent["message"]
        self.delay = consequent["delay"]
        self.order = consequent["order"]
