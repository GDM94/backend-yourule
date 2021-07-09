import redis
from os.path import dirname, join, abspath
import configparser
import json
from datetime import datetime
from .dto.AntecedentEvaluationDTO import AntecedentEvaluation


class LastTimeOnEvaluation(object):
    def __init__(self, mqtt_client):
        config = self.read_config()
        HOST = config.get("REDIS", "host")
        PORT = config.get("REDIS", "port")
        self.EXPIRATION = config.get("REDIS", "expiration")
        self.r = redis.Redis(host=HOST, port=PORT, decode_responses=True)
        self.mqtt_client = mqtt_client

    def read_config(self):
        d = dirname(dirname(dirname(abspath(__file__))))
        config_path = join(d, 'properties', 'app-config.ini')
        config = configparser.ConfigParser()
        config.read(config_path)
        return config

    def get_all_users(self):
        users_keys = self.r.scan(0, "user:name:*:id", 1000)[1]
        user_id_list = []
        for user_key in users_keys:
            user_id = self.r.get(user_key)
            user_id_list.append(user_id)
        return user_id_list

    def get_rules_with_last_time_measure(self, user_id):
        rule_id_list = self.r.scan(0, "user:" + user_id + ":rule:*:name", 1000)[1]
        selection = {}
        for rule_id_key in rule_id_list:
            rule_id = rule_id_key.split(":")[3]
            selection[rule_id] = []
            antecedent_keys = self.r.scan(0, "user:" + user_id + ":rule:" + rule_id + ":antecedent:*:measure", 1000)[1]
            for antecedent_key in antecedent_keys:
                measure = self.r.get(antecedent_key)
                if measure == "last time on":
                    device_id = antecedent_key.split(":")[-2]
                    selection[rule_id].append(device_id)
            if not selection[rule_id]:
                del selection[rule_id]
        return selection

    def last_value_on_trigger(self):
        user_id_list = self.get_all_users()
        for user_id in user_id_list:
            output = AntecedentEvaluation(user_id, [])
            rule_set = set([])
            selection = self.get_rules_with_last_time_measure(user_id)
            for rule_id in selection.keys():
                devices_list = selection[rule_id]
                for device_id in devices_list:
                    trigger = self.last_time_on_evaluation(user_id, rule_id, device_id)
                    if trigger:
                        rule_set.add(rule_id)
            output.rules = list(rule_set)
            if len(output.rules) > 0:
                payload = json.dumps(output, default=lambda o: o.__dict__)
                self.mqtt_client.publish(payload)

    def last_time_on_evaluation(self, user_id, rule_id, device_id):
        trigger = False
        pattern_key = "user:" + user_id + ":rule:" + rule_id + ":antecedent:" + device_id
        old_evaluation = self.r.get(pattern_key + ":evaluation")
        # time now
        measure_now_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        measure_now = datetime.strptime(measure_now_str, '%d/%m/%Y %H:%M:%S')
        # delta time last on
        device_last_on = self.r.get("device:" + device_id + ":last_on")
        measure_time_last_on = datetime.strptime(device_last_on, '%d/%m/%Y %H:%M:%S')
        time_delta_on = (measure_now - measure_time_last_on).total_seconds()
        # delta time last off
        device_last_off = self.r.get("device:" + device_id + ":last_off")
        measure_time_last_off = datetime.strptime(device_last_off, '%d/%m/%Y %H:%M:%S')
        time_delta_off = (measure_now - measure_time_last_off).total_seconds()
        # time reference
        time0 = datetime.strptime("00:00", '%H:%M')
        # delta time threshold start
        start_value_str = self.r.get(pattern_key + ":start_value")
        start_value = datetime.strptime(start_value_str, '%H:%M')
        time_ref_start = (start_value - time0).total_seconds()
        # delta time threshold stop
        stop_value_str = self.r.get(pattern_key + ":stop_value")
        stop_value = datetime.strptime(stop_value_str, '%H:%M')
        time_ref_stop = (stop_value - time0).total_seconds()
        device_measure = self.r.get("device:" + device_id + ":measure")
        new_measure = "off"
        evaluation = "false"
        if device_measure == "on":
            if time_delta_off <= time_ref_stop:
                evaluation = "true"
                new_measure = "on"
        else:
            if time_delta_on >= time_ref_start:
                evaluation = "true"
                new_measure = "on"
        if new_measure != device_measure:
            self.r.set(pattern_key + ":evaluation", evaluation)
            trigger = True
        return trigger
