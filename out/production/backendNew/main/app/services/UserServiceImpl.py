from ruleapp.Profile.ProfileDTO import ProfileDto
from ruleapp.Profile.ProfileFunctions import ProfileFunction
from ruleapp.Devices.Alert.AlertFunctions import AlertFunction
from ruleapp.Devices.Timer.TimerFunctions import TimerFunction
from ruleapp.Devices.Weather.WeatherFunctions import WeatherFunction
import requests
from ruleapp.Devices.Weather.WeatherResponseDTO import WeatherResponse
import json
from .StructDTO import Struct


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
        self.weather_functions = WeatherFunction(redis, self.api_key, self.api_location_url, self.api_weather_url)

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
            if output != "false" and output != "error":
                self.timer_functions.register(profile.user_id)
                self.alert_functions.register(profile.user_id, profile.email)
                self.weather_functions.register(profile.user_id)
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
        return self.weather_functions.set_location(user_id, name, country, lat, lon)

    def get_user_location(self, user_id):
        return self.weather_functions.get_location(user_id)

    def search_new_location(self, name):
        return self.weather_functions.search_new_location(name)
