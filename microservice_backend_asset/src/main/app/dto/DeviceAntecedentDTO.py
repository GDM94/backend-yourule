
class DeviceAntecedent(object):
    def __init__(self, device_id, name, measure, max_measure, error_setting, rules):
        self.id = device_id
        self.name = name
        self.measure = measure
        self.setting = max_measure
        self.error = error_setting
        self.rules = rules
