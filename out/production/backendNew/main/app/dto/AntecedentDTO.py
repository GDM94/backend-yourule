

class Antecedent(object):
    def __init__(self, device_id, device_name, start_value, stop_value, condition, evaluation, measure, value, order):
        self.device_id = device_id
        self.name = device_name
        self.start_value = start_value
        self.stop_value = stop_value
        self.condition = condition
        self.evaluation = evaluation
        self.measure = measure
        self.value = value
        self.order = order

