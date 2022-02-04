from .AlertConsequentDTO import AlertConsequent
import smtplib
from email.mime.text import MIMEText


def email_connection(email_user, email_password):
    print("email connection")
    session = smtplib.SMTP("smtp.gmail.com", 587)
    session.starttls()
    session.login(email_user, email_password)
    return session


class AlertConsequentFunction(object):
    def __init__(self, redis):
        self.r = redis
        self.email_user = "raspberrypi.sugherotorto"
        self.email_password = "giomartagio"

    def get_consequent(self, user_id, rule_id, device_id):
        try:
            consequent = AlertConsequent()
            key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_consequents:" + device_id
            consequent.device_id = device_id
            consequent.device_name = self.r.get("device:" + device_id + ":name")
            consequent.message = self.r.get(key_pattern + ":message")
            consequent.delay = self.r.get(key_pattern + ":delay")
            consequent.order = self.r.get(key_pattern + ":order")
            return consequent
        except Exception as error:
            print(repr(error))
            return "error"

    def get_consequent_slim(self, user_id, rule_id, device_id):
        try:
            consequent = AlertConsequent()
            key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_consequents:" + device_id
            consequent.device_id = device_id
            consequent.device_name = self.r.get("device:" + device_id + ":name")
            consequent.order = self.r.get(key_pattern + ":order")
            consequent.delay = self.r.get(key_pattern + ":delay")
            return consequent
        except Exception as error:
            print(repr(error))
            return "error"

    def delete_consequent(self, user_id, rule_id, device_id):
        try:
            self.r.lrem("device:" + device_id + ":rules", rule_id)
            self.r.lrem("user:" + user_id + ":rule:" + rule_id + ":device_consequents", device_id)
            key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_consequents:" + device_id
            self.r.delete(key_pattern + ":message")
            self.r.delete(key_pattern + ":delay")
            self.r.delete(key_pattern + ":order")
            return "true"
        except Exception as error:
            print(repr(error))
            return "error"

    def add_consequent(self, user_id, rule_id, device_id):
        try:
            device_consequents = self.r.lrange("user:" + user_id + ":rule:" + rule_id + ":device_consequents")
            result = "false"
            if device_id not in device_consequents:
                consequent = AlertConsequent()
                consequent.order = str(len(device_consequents))
                self.r.rpush("device:" + device_id + ":rules", rule_id)
                self.r.rpush("user:" + user_id + ":rule:" + rule_id + ":device_consequents", device_id)
                key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_consequents:" + device_id
                self.r.set(key_pattern + ":message", consequent.message)
                self.r.set(key_pattern + ":delay", consequent.delay)
                self.r.set(key_pattern + ":order", consequent.order)
                result = "true"
            return result
        except Exception as error:
            print(repr(error))
            return "error"

    def update_consequent(self, user_id, rule_id, new_consequent):
        try:
            consequent = AlertConsequent()
            consequent.consequent_mapping(new_consequent)
            device_consequents = self.r.lrange("user:" + user_id + ":rule:" + rule_id + ":device_consequents")
            result = "false"
            if consequent.device_id in device_consequents:
                key_pattern = "user:" + user_id + ":rule:" + rule_id + ":rule_consequents:" + consequent.device_id
                self.r.set(key_pattern + ":message", consequent.message)
                self.r.set(key_pattern + ":delay", consequent.delay)
                self.r.set(key_pattern + ":order", consequent.order)
                result = "true"
            return result
        except Exception as error:
            print(repr(error))
            return "error"

    def alert_evaluation(self, user_id, rule_id):
        if self.r.get("user:" + user_id + ":rule:" + rule_id + ":evaluation") == "true":
            alert_id = "alert-" + user_id
            sendto = self.r.lrange("device:" + alert_id + ":email_list")
            if len(sendto) > 0:
                alert = email_connection(self.email_user, self.email_password)
                rule_name = self.r.get("user:" + user_id + ":rule:" + rule_id + ":name")
                sender = "raspberrypi.sugherotorto@gmail.com"
                content = self.r.get(
                    "user:" + user_id + ":rule:" + rule_id + ":rule_consequents:" + alert_id + ":message")
                msg = MIMEText(content, 'plain')
                msg['Subject'] = "ALERT RULEAPP: " + rule_name
                msg['From'] = sender
                alert.sendmail(sender, sendto, msg.as_string())
                alert.quit()
                print("send alert email")
