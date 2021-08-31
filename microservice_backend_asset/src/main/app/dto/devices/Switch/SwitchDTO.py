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
        self.status = "initialization"
        self.color = "yellow"
