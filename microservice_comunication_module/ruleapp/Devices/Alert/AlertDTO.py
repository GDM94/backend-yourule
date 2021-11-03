
class Alert(object):
    def __init__(self):
        self.id = ""
        self.name = "alert"
        self.email_list = []
        self.rules = []
        self.status = "connected"
        self.color = "green"
        self.expiration = "no"

    def device_mapping(self, device):
        self.id = device["id"]
        self.name = device["name"]
        self.rules = device["rules"]
        self.email_list = device["email_list"]
