
class Alert(object):
    def __init__(self):
        self.device_id = ""
        self.name = "alert"
        self.email_list = []
        self.rules = []
        self.status = "connected"
        self.color = "green"
        self.expire_time = "10"

    def device_mapping(self, device):
        self.device_id = device["device_id"]
        self.name = device["name"]
        self.rules = device["rules"]
        self.email_list = device["email_list"]
