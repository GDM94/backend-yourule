from ..WeatherAntecedentDTO import CloudAntecedent


class CloudAntecedentFunction(object):
    def __init__(self, redis):
        self.r = redis

    def get_cloud_antecedent(self, user_id, rule_id, device_id):
        dto = CloudAntecedent()
        key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_antecedents:" + device_id
        dto.check_clouds = self.r.get(key_pattern + ":check_clouds")
        dto.clouds_condition = self.r.get(key_pattern + ":clouds_condition")
        dto.clouds_start_value = self.r.get(key_pattern + ":clouds_start_value")
        dto.clouds_stop_value = self.r.get(key_pattern + ":clouds_stop_value")
        dto.cloud_evaluation = self.r.get(key_pattern + ":cloud_evaluation")
        location_name = self.r.get("user:" + user_id + ":location:name")
        dto.clouds_value = self.r.get("weather:" + location_name + ":clouds")
        return dto

    def set_cloud_antecedent(self, user_id, rule_id, device_id, dto: CloudAntecedent):
        key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_antecedents:" + device_id
        self.r.set(key_pattern + ":check_clouds", dto.check_clouds)
        self.r.set(key_pattern + ":clouds_condition", dto.clouds_condition)
        self.r.set(key_pattern + ":clouds_start_value", dto.clouds_start_value)
        self.r.set(key_pattern + ":clouds_stop_value", dto.clouds_stop_value)
        self.r.set(key_pattern + ":cloud_evaluation", dto.cloud_evaluation)

    def delete_cloud_antecedent(self, user_id, rule_id, device_id):
        key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_antecedents:" + device_id
        self.r.delete(key_pattern + ":check_clouds")
        self.r.delete(key_pattern + ":clouds_condition")
        self.r.delete(key_pattern + ":clouds_start_value")
        self.r.delete(key_pattern + ":clouds_stop_value")
        self.r.delete(key_pattern + ":cloud_evaluation")

    def register_cloud_antecedent(self, user_id, rule_id, device_id):
        key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_antecedents:" + device_id
        dto = CloudAntecedent()
        self.r.set(key_pattern + ":check_clouds", dto.check_clouds)
        self.r.set(key_pattern + ":clouds_condition", dto.clouds_condition)
        self.r.set(key_pattern + ":clouds_start_value", dto.clouds_start_value)
        self.r.set(key_pattern + ":clouds_stop_value", dto.clouds_stop_value)
        self.r.set(key_pattern + ":cloud_evaluation", dto.cloud_evaluation)

    def clouds_antecedent_evaluation(self, user_id, rule_id, device_id):
        try:
            dto = self.get_cloud_antecedent(user_id, rule_id, device_id)
            evaluation = "true"
            if dto.check_clouds == "true":
                evaluation = "false"
                if dto.clouds_condition == "between":
                    if int(dto.clouds_start_value) < int(dto.clouds_value) <= int(dto.clouds_stop_value):
                        evaluation = "true"
                elif dto.clouds_condition == ">":
                    if int(dto.clouds_value) > int(dto.clouds_start_value):
                        evaluation = "true"
                elif dto.clouds_condition == "<":
                    if int(dto.clouds_value) < int(dto.clouds_stop_value):
                        evaluation = "true"
                if dto.cloud_evaluation != evaluation:
                    key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_antecedents:" + device_id
                    self.r.set(key_pattern + ":cloud_evaluation", evaluation)
            return evaluation
        except Exception as error:
            print(repr(error))
            return "false"
