import jwt
from ..dto.LocationDTO import Location
import requests


class UserService(object):
    def __init__(self, secret_key, redis, config):
        self.secret_key = secret_key
        self.r = redis
        self.api_key = config.get("OPEN_WEATHER", "api_key")
        self.api_location_url = config.get("OPEN_WEATHER", "api_location_url")

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
                # self.weather_registration(user_id)
                self.alert_registration(user_id, email)
                self.set_user_location(user_id, "Torino", "IT", "45.1333", "7.3667")
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
        self.r.rpush("user:" + user_id + ":antecedents", timer_id)
        self.r.set("device:" + timer_id + ":userid", user_id)
        self.r.set("device:" + timer_id + ":name", "timer")

    def alert_registration(self, user_id, email):
        alert_id = "alert" + user_id
        self.r.rpush("user:" + user_id + ":consequents", alert_id)
        self.r.set("device:" + alert_id + ":userid", user_id)
        self.r.set("device:" + alert_id + ":name", "alert")
        self.r.set("device:" + alert_id + ":automatic", "true")
        self.r.lpush("device:" + alert_id + ":email_list", email)

    def weather_registration(self, user_id):
        weather_id = "weather" + user_id
        self.r.rpush("user:" + user_id + ":antecedents", weather_id)
        self.r.set("device:" + weather_id + ":userid", user_id)
        self.r.set("device:" + weather_id + ":name", "weather")

    def get_user_names(self):
        try:
            users_keys = self.r.scan("user:name:*:id")
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

    def set_user_location(self, user_id, name, country, lat, lon):
        key_pattern = "user:" + user_id + ":location:"
        try:
            self.r.set(key_pattern + "name", name)
            self.r.set(key_pattern + "country", country)
            self.r.set(key_pattern + "lat", lat)
            self.r.set(key_pattern + "lon", lon)
        except Exception as error:
            print(repr(error))
            return "error"
        else:
            return ""

    def get_user_location(self, user_id):
        key_pattern = "user:" + user_id + ":location:"
        try:
            name = self.r.get(key_pattern + "name")
            country = self.r.get(key_pattern + "country")
            lat = self.r.get(key_pattern + "lat")
            lon = self.r.get(key_pattern + "lon")
            output = Location(name, country, lat, lon)
        except Exception as error:
            print(repr(error))
            return "error"
        else:
            return output

    def search_new_location(self, name):
        try:
            r = requests.get(self.api_location_url, params={'q': name, 'limit': 5, 'appid': self.api_key})
            data = r.json()
        except Exception as error:
            print(repr(error))
            return "error"
        else:
            return data
