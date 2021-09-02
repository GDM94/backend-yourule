import json


class Button(object):
    def __init__(self):
        self.device_id = ""
        self.name = "BUTTON"
        self.measure = "-"
        self.expiration = "10"
        self.rules = []
        self.status = "disconnected"
        self.color = "red"
        self.unit_measure = ""
        self.last_time_on = "-"
        self.last_time_off = "-"
        self.last_date_on = "-"
        self.last_date_off = "-"

    def json_mapping(self, device_json):
        x = json.loads(device_json)
        if "device_id" in x.keys():
            self.device_id = x["device_id"]
        if "name" in x.keys():
            self.name = x["name"]
        if "expiration" in x.keys():
            self.expiration = x["expiration"]
        if "rules" in x.keys():
            self.rules = x["rules"]