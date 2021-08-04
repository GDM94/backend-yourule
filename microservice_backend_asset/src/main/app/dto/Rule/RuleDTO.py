class RuleDto(object):
    def __init__(self):
        self.rule_id = ""
        self.rule_name = ""
        self.last_time_on = ""
        self.last_time_off = ""
        self.last_date_on = ""
        self.last_date_off = ""
        self.device_antecedents = []
        self.device_consequents = []
        self.antecedents = []
        self.consequents = []
        self.evaluation = "false"
