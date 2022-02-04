class Rule(object):
    def __init__(self):
        self.id = ""
        self.name = ""
        self.last_time_on = "-"
        self.last_time_off = "-"
        self.last_date_on = "-"
        self.last_date_off = "-"
        self.device_antecedents = []
        self.device_consequents = []
        self.rule_antecedents = []
        self.rule_consequents = []
        self.evaluation = "false"

    def json_mapping(self, rule_json):
        self.id = rule_json["id"]
        self.name = rule_json["name"]
        self.device_antecedents = rule_json["device_antecedents"]
        self.device_consequents = rule_json["device_consequents"]
        self.rule_antecedents = rule_json["rule_antecedents"]
        self.rule_consequents = rule_json["rule_consequents"]
