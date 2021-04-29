
class Consequent(object):
    def __init__(self, device_id, device_name, if_value, else_value, automatic, measure):
        self.device_id = device_id
        self.name = device_name
        self.if_value = if_value
        self.else_value = else_value
        self.automatic = automatic
        self.measure = measure

