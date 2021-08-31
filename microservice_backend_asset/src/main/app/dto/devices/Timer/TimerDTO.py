class Timer(object):
    def __init__(self):
        self.device_id = ""
        self.name = "timer"
        self.measure_time = ""
        self.measure_day = ""
        self.rules = []
        self.status = "connected"
        self.color = "green"

    def constructor(self, user_id, name, rules):
        self.device_id = "timer"+user_id
        self.name = name
        self.rules = rules

    def constructor_register(self, user_id):
        self.device_id = "timer"+user_id
