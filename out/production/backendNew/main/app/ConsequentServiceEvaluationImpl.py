import smtplib
from email.mime.text import MIMEText
import json


def email_connection(email_user, email_password):
    print("email connection")
    session = smtplib.SMTP("smtp.gmail.com", 587)
    session.starttls()
    session.login(email_user, email_password)
    return session


class ConsequentServiceEvaluation(object):
    def __init__(self, config, redis):
        self.r = redis
        self.email_user = config.get("ALERT", "email_user")
        self.email_password = config.get("ALERT", "email_password")

    def switch_evaluation(self, user_id, device_id, delay, output):
        key_pattern = "device:" + device_id
        automatic = self.r.get(key_pattern + ":automatic")
        if automatic == "true":
            rules = list(self.r.smembers(key_pattern + ":rules"))
            new_status = "off"
            for rule in rules:
                rule_evaluation = self.r.get("user:" + user_id + ":rule:" + rule + ":evaluation")
                if rule_evaluation == "true":
                    new_status = "on"
                    break
            if self.r.exists(key_pattern + ":measure") == 1:
                current_status = self.r.get("device:" + device_id + ":measure")
                if current_status != new_status:
                    output["device_id"].append(device_id)
                    output["measure"].append(new_status)
                    output["delay"].append(delay)
        return output

    def alert_evaluation(self, user_id, rule_id):
        if self.r.get("user:" + user_id + ":rule:" + rule_id + ":evaluation") == "true":
            alert_id = "alert" + user_id
            sendto = self.r.lrange("device:" + alert_id + ":email_list")
            if len(sendto) > 0:
                alert = email_connection(self.email_user, self.email_password)
                rule_name = self.r.get("user:" + user_id + ":rule:" + rule_id + ":name")
                sender = "raspberrypi.sugherotorto@gmail.com"
                content = """Alert for rule name {}""".format(rule_name)
                msg = MIMEText(content, 'plain')
                msg['Subject'] = "ALERT YOURULE"
                msg['From'] = sender
                alert.sendmail(sender, sendto, msg.as_string())
                alert.quit()
                print("send alert email")

    def consequent_order_delay(self, user_id, rule_id, consequent_keys):
        pattern_key = "user:" + user_id + ":rule:" + rule_id
        consequent_list_unordered = []
        for key in consequent_keys:
            consequent_obj = {}
            device_id = key.split(":")[-2]
            order = self.r.get(pattern_key + ":consequent:" + device_id + ":order")
            delay = self.r.get(pattern_key + ":consequent:" + device_id + ":delay")
            consequent_obj["device_id"] = device_id
            consequent_obj["order"] = int(order)
            consequent_obj["delay"] = int(delay)
            consequent_list_unordered.append(consequent_obj)
        consequent_list_ordered = sorted(consequent_list_unordered, key=lambda k: k['order'])
        delay = 0
        consequent_list_ordered_delay = []
        for consequent in consequent_list_ordered:
            delay = delay + consequent["delay"]
            consequent["delay"] = delay
            consequent_list_ordered_delay.append(consequent)
        return consequent_list_ordered_delay

    def consequent_evaluation(self, payload):
        try:
            trigger = json.loads(payload)
            user_id = str(trigger["user_id"])
            rule_id = str(trigger["rule_id"])
            output = {"device_id": [], "measure": [], "delay": []}
            pattern_key = "user:" + user_id + ":rule:" + rule_id
            consequent_keys = self.r.scan(pattern_key + ":consequent:*:order")
            consequent_list_ordered_delay = self.consequent_order_delay(user_id, rule_id, consequent_keys)
            for consequent in consequent_list_ordered_delay:
                device_id = consequent["device_id"]
                delay = str(consequent["delay"])
                if "alert" not in device_id:
                    output = self.switch_evaluation(user_id, device_id, delay, output)
                else:
                    self.alert_evaluation(user_id, rule_id)
        except Exception as error:
            print(repr(error))
            return output
        else:
            return output
