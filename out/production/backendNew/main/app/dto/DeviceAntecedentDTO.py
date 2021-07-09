class DeviceAntecedent(object):
    def __init__(self, device_id, name, measure, setting, error_setting, rules, absolute_measure, max_measure,
                 min_measure, max_measure_time, min_measure_time):
        self.id = device_id
        self.name = name
        self.measure = measure
        self.setting = setting
        self.error = error_setting
        self.rules = rules
        self.absolute_measure = absolute_measure
        self.max_measure = max_measure
        self.min_measure = min_measure
        self.max_measure_time = max_measure_time
        self.min_measure_time = min_measure_time

