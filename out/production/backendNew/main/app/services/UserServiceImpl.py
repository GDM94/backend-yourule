from ruleapp.LocationDTO import Location
import requests
from ruleapp.Profile.ProfileDTO import ProfileDto
from ruleapp.Profile.ProfileFunctions import ProfileFunction
from ruleapp.Devices.Alert.AlertFunctions import AlertFunction
from ruleapp.Devices.Timer.TimerFunctions import TimerFunction


class UserService(object):
    def __init__(self, secret_key, redis, config):
        self.secret_key = secret_key
        self.r = redis
        self.api_key = config.get("OPEN_WEATHER", "api_key")
        self.api_location_url = config.get("OPEN_WEATHER", "api_location_url")
        password_key = config.get("OAUTH", "password_key")
        token_key = config.get("OAUTH", "token_key")
        self.profile_functions = ProfileFunction(redis, password_key, token_key)
        self.timer_functions = TimerFunction(redis)
        self.alert_functions = AlertFunction(redis)

    def user_login(self, profile_map):
        try:
            output = {"tokenId": "false"}
            profile = ProfileDto()
            profile.constructor_map(profile_map)
            token = self.profile_functions.login(profile)
            output["tokenId"] = token
        except Exception as error:
            print(repr(error))
            return "error"
        else:
            return output

    def user_registration(self, profile_map):
        try:
            output = {"tokenId": "false"}
            profile = ProfileDto()
            profile.constructor_map(profile_map)
            token = self.profile_functions.login(profile)
            output["tokenId"] = token
            if profile.user_id:
                self.timer_functions.register(profile.user_id)
                # self.weather_registration(profile.user_id)
                self.alert_functions.register(profile.user_id, profile.email)
                self.set_user_location(profile.user_id, "Torino", "IT", "45.1333", "7.3667")
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

    def weather_registration(self, user_id):
        weather_id = "weather" + user_id
        self.r.rpush("user:" + user_id + ":antecedents", weather_id)
        self.r.set("device:" + weather_id + ":userid", user_id)
        self.r.set("device:" + weather_id + ":name", "weather")

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
