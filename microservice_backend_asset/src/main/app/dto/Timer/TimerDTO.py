class Timer(object):
    def __init__(self):
        self.device_id = ""
        self.name = "timer"
        self.measure_time = ""
        self.measure_day = ""
        self.rules = []
        self.status = "connected"
        self.color = "green"

    def constructor(self, device_id, name, rules):
        self.device_id = device_id
        self.name = name
        self.rules = rules
