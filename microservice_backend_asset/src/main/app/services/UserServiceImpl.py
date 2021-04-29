import redis
from os.path import dirname, join, abspath
import configparser
import jwt


class UserService(object):
    def __init__(self):
        config = self.read_config()
        redis_host = config.get("REDIS", "host")
        redis_port = config.get("REDIS", "port")
        self.secret_key = config.get("OAUTH", "secret")
        self.r = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)

    def read_config(self):
        d = dirname(dirname(dirname(dirname(abspath(__file__)))))
        config_path = join(d, 'properties', 'app-config.ini')
        config = configparser.ConfigParser()
        config.read(config_path)
        return config

    def user_login(self, email, password):
        try:
            key_pattern = "user:name:" + email
            output = {"tokenId": "false"}
            if self.r.exists(key_pattern + ":id") == 1:
                user_password = self.r.get(key_pattern + ":password")
                if password == user_password:
                    self.r.set("user:name:" + email + ":login", "true")
                    user_id = self.r.get(key_pattern + ":id")
                    name = self.r.get(key_pattern + ":name")
                    surname = self.r.get(key_pattern + ":surname")
                    payload = {"uid": user_id, "email": email, "password": password, "name": name, "surname": surname}
                    output["tokenId"] = jwt.encode(payload, self.secret_key, algorithm="HS256")
        except Exception as error:
            print(repr(error))
            return "error"
        else:
            return output

    def user_registration(self, email, password, name, surname):
        try:
            output = {"tokenId": "false"}
            user_counter = "user:counter"
            if self.r.exists("user:name:" + email + ":id") == 0:
                user_id = str(self.r.incr(user_counter))
                self.r.set("user:name:" + email + ":id", user_id)
                self.r.set("user:name:" + email + ":password", password)
                self.r.set("user:name:" + email + ":name", name)
                self.r.set("user:name:" + email + ":surname", surname)
                self.r.set("user:name:" + email + ":login", "true")
                self.timer_registration(user_id)
                self.alert_registration(user_id)
                payload = {"uid": user_id, "email": email, "password": password, "name": name, "surname": surname}
                output["tokenId"] = jwt.encode(payload, self.secret_key, algorithm="HS256")
        except Exception as error:
            print(repr(error))
            return "error"
        else:
            return output

    def get_user_id(self, user_name):
        try:
            output = self.r.get("user:name:" + user_name + ":id")
        except Exception as error:
            print(repr(error))
            return "error"
        else:
            return output

    def timer_registration(self, user_id):
        timer_id = "timer" + user_id
        self.r.sadd("user:" + user_id + ":antecedents", timer_id)
        self.r.set("device:" + timer_id + ":userid", user_id)
        self.r.set("device:" + timer_id + ":name", "timer")

    def alert_registration(self, user_id):
        alert_id = "alert" + user_id
        self.r.sadd("user:" + user_id + ":consequents", alert_id)
        self.r.set("device:" + alert_id + ":userid", user_id)
        self.r.set("device:" + alert_id + ":name", "alert")
        self.r.set("device:" + alert_id + ":automatic", "true")

    def get_user_names(self):
        try:
            users_keys = self.r.scan(0, "user:name:*:id", 1000)[1]
            output = []
            if len(users_keys) > 0:
                for key in users_keys:
                    user_name = key.split(":")[-2]
                    output.append(user_name)
        except Exception as error:
            print(repr(error))
            return "error"
        else:
            return output

    def get_user_logged(self, user_name):
        try:
            output = "false"
            if self.r.exists("user:name:" + user_name + ":id"):
                output = self.r.get("user:name:" + user_name + ":login")
        except Exception as error:
            print(repr(error))
            return "error"
        else:
            return output

    def user_logout(self, user_name):
        self.r.set("user:name:" + user_name + ":login", "false")
