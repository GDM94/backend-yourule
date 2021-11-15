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
        self.api_weather_url = config.get("OPEN_WEATHER", "api_weather_url")
        token_key = config.get("OAUTH", "token_key")
        self.profile_functions = ProfileFunction(redis, token_key)
        self.timer_functions = TimerFunction(redis)
        self.alert_functions = AlertFunction(redis)

    def user_login(self, profile_map):
        try:
            profile = ProfileDto()
            profile.constructor_map(profile_map)
            output = self.profile_functions.login(profile)
            return output
        except Exception as error:
            print(repr(error))
            return "error"

    def user_registration(self, profile_map):
        try:
            profile = ProfileDto()
            profile.constructor_map(profile_map)
            output = self.profile_functions.register(profile)
            print(output)
            if output != "false" and output != "error":
                self.timer_functions.register(profile.user_id)
                self.alert_functions.register(profile.user_id, profile.email)
                self.set_user_location(profile.user_id, "Torino", "IT", "45.1333", "7.3667")
            return output
        except Exception as error:
            print(repr(error))
            return "error"

    def get_user_id(self, user_name):
        try:
            output = self.r.get("user:name:" + user_name + ":id")
        except Exception as error:
            print(repr(error))
            return "error"
        else:
            return output

    def set_user_location(self, user_id, name, country, lat, lon):
        key_pattern = "user:" + user_id + ":location:"
        try:
            self.r.set(key_pattern + "name", name)
            self.r.set(key_pattern + "country", country)
            self.r.set(key_pattern + "lat", lat)
            self.r.set(key_pattern + "lon", lon)
            return "true"
        except Exception as error:
            print(repr(error))
            return "error"

    def get_user_location(self, user_id):
        key_pattern = "user:" + user_id + ":location:"
        try:
            name = self.r.get(key_pattern + "name")
            country = self.r.get(key_pattern + "country")
            lat = self.r.get(key_pattern + "lat")
            lon = self.r.get(key_pattern + "lon")
            output = Location(name, country, lat, lon)
            return output
        except Exception as error:
            print(repr(error))
            return "error"

    def search_new_location(self, name):
        try:
            r = requests.get(self.api_location_url, params={'q': name, 'limit': 5, 'appid': self.api_key})
            data = r.json()
            return data
        except Exception as error:
            print(repr(error))
            return "error"
