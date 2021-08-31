class Alert(object):
    def __init__(self):
        self.device_id = ""
        self.name = "alert"
        self.email_list = []
        self.rules = []
        self.status = "connected"
        self.color = "green"

    def constructor(self, device_id, name, email_list, rules):
        self.device_id = device_id
        self.name = name
        self.email_list = email_list
        self.rules = rules
