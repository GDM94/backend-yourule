
class AlertConsequent(object):
    def __init__(self, device_id, name, rules, email_list):
        self.id = device_id
        self.name = name
        self.rules = rules
        self.email_list = email_list
