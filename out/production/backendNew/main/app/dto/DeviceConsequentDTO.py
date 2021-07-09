
class DeviceConsequent(object):
    def __init__(self, device_id, name, measure, rules, last_on, last_off, automatic, manual_measure):
        self.id = device_id
        self.name = name
        self.measure = measure
        self.rules = rules
        self.last_on = last_on
        self.last_off = last_off
        self.automatic = automatic
        self.manual_measure = manual_measure
