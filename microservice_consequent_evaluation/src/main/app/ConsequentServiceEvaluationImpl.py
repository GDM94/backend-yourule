import smtplib
from email.mime.text import MIMEText
import redis
from os.path import dirname, join, abspath
import configparser
import json


class ConsequentServiceEvaluation(object):
    def __init__(self):
        config = self.read_config()
        HOST = config.get("REDIS", "host")
        PORT = config.get("REDIS", "port")
        self.EXPIRATION = config.get("REDIS", "expiration")
        self.r = redis.Redis(host=HOST, port=PORT, decode_responses=True)
        self.email_user = config.get("ALERT", "email_user")
        self.email_password = config.get("ALERT", "email_password")

    def read_config(self):
        d = dirname(dirname(dirname(abspath(__file__))))
        config_path = join(d, 'properties', 'app-config.ini')
        config = configparser.ConfigParser()
        config.read(config_path)
        return config

    def email_connection(self, email_user, email_password):
        print("email connection")
        session = smtplib.SMTP("smtp.gmail.com", 587)
        session.starttls()
        session.login(email_user, email_password)
        return session

    def switch_evaluation(self, user_id, device_id, output):
        key_pattern = "device:" + device_id
        automatic = self.r.get(key_pattern + ":automatic")
        if automatic == "true":
            rules = list(self.r.smembers(key_pattern + ":rules"))
            consequent_evaluation = "false"
            for rule in rules:
                if self.r.get("user:" + user_id + ":rule:" + rule + ":evaluation") == "true":
                    consequent_evaluation = "true"
                    break
            new_status = "off"
            if consequent_evaluation == "true":
                new_status = "on"
            if self.r.exists(key_pattern + ":measure") == 1:
                current_status = self.r.get("device:" + device_id + ":measure")
                if current_status != new_status:
                    output["device_id"].append(device_id)
                    output["measure"].append(new_status)
        return output

    def alert_evaluation(self, user_id, rule_id):
        if self.r.get("user:" + user_id + ":rule:" + rule_id + ":evaluation") == "true":
            alert_id = "alert" + user_id
            sendto = list(self.r.smembers("device:" + alert_id + ":email_list"))
            if len(sendto) > 0:
                alert = self.email_connection(self.email_user, self.email_password)
                rule_name = self.r.get("user:" + user_id + ":rule:" + rule_id + ":name")
                sender = "raspberrypi.sugherotorto@gmail.com"
                content = """Alert for rule name {}""".format(rule_name)
                msg = MIMEText(content, 'plain')
                msg['Subject'] = "ALERT YOURULE"
                msg['From'] = sender
                alert.sendmail(sender, sendto, msg.as_string())
                alert.quit()
                print("send alert email")

    def consequent_evaluation(self, payload):
        try:
            trigger = json.loads(payload)
            user_id = str(trigger["user_id"])
            rule_id = str(trigger["rule_id"])
            output = {"device_id": [], "measure": []}
            pattern_key = "user:" + user_id + ":rule:" + rule_id
            consequent_keys = self.r.scan(0, pattern_key + ":consequent:*:if_value", 1000)[1]
            for key in consequent_keys:
                device_id = key.split(":")[-2]
                if "alert" not in device_id:
                    output = self.switch_evaluation(user_id, device_id, output)
                else:
                    self.alert_evaluation(user_id, rule_id)
        except Exception as error:
            print(repr(error))
            return output
        else:
            return output
