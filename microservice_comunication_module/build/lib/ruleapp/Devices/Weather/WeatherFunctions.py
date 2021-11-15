import requests
from .WeatherResponseDTO import WeatherResponse
import json
from .LocationDTO import Location


class WeatherFunction(object):
    def __init__(self, redis, api_key, api_location_url, api_weather_url):
        self.r = redis
        self.api_key = api_key
        self.api_location_url = api_location_url
        self.api_weather_url = api_weather_url

    def get_device(self, user_id):
        try:
            key_pattern = "user:" + user_id + ":location:"
            lat = self.r.get(key_pattern + "lat")
            lon = self.r.get(key_pattern + "lon")
            r = requests.get(self.api_weather_url, params={'lat': lat, 'lon': lon, 'appid': self.api_key})
            data = r.json()
            weather_response = json.loads(data, object_hook=lambda d: WeatherResponse(**d))
            print(weather_response)
            return data
        except Exception as error:
            print(repr(error))
            return "error"

    def register(self, user_id):
        try:
            device_id = "WEATHER-" + user_id
            key_pattern = "device:" + device_id
            if self.r.exists(key_pattern + ":name") == 0:
                self.r.set(key_pattern + ":name", "WEATHER")
                self.r.set(key_pattern + ":user_id", user_id)
                self.set_location(user_id, "Torino", "IT", "45.1333", "7.3667")
                return "true"
            else:
                return "false"
        except Exception as error:
            print(repr(error))
            return "error"

    def set_location(self, user_id, name, country, lat, lon):
        try:
            device_id = "WEATHER-" + user_id
            key_pattern = "device:" + device_id + ":location"
            self.r.set(key_pattern + ":name", name)
            self.r.set(key_pattern + ":country", country)
            self.r.set(key_pattern + ":lat", lat)
            self.r.set(key_pattern + ":lon", lon)
            return "true"
        except Exception as error:
            print(repr(error))
            return "error"

    def get_location(self, user_id):
        try:
            device_id = "WEATHER-" + user_id
            key_pattern = "device:" + device_id + ":location"
            name = self.r.get(key_pattern + ":name")
            country = self.r.get(key_pattern + ":country")
            lat = self.r.get(key_pattern + ":lat")
            lon = self.r.get(key_pattern + ":lon")
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
