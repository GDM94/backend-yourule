import requests
from .WeatherResponseDTO import WeatherResponse
from .LocationDTO import Location
from munch import DefaultMunch
from .WeatherDTO import Weather
from datetime import datetime
from ..DeviceId import WEATHER


class WeatherFunction(object):
    def __init__(self, redis, config):
        self.r = redis
        self.api_key = config.get("OPEN_WEATHER", "api_key")
        self.api_location_url = config.get("OPEN_WEATHER", "api_location_url")
        self.api_weather_url = config.get("OPEN_WEATHER", "api_weather_url")
        self.weather_refresh_cycle = 60 * 60

    def register(self, user_id):
        try:
            device_id = WEATHER + "-" + user_id
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

    def get_device(self, user_id, device_id):
        try:
            weather = Weather()
            weather.id = device_id
            weather.name = self.r.get("device:" + device_id + ":name")
            # location
            weather.location_name = self.r.get("user:" + user_id + ":location:name")
            location_key_pattern = "weather:location:" + weather.location_name
            weather.country = self.r.get(location_key_pattern + ":country")
            weather.lat = self.r.get(location_key_pattern + ":lat")
            weather.lon = self.r.get(location_key_pattern + ":lon")
            # weather
            key_pattern = "weather:" + weather.location_name
            weather.icon = list(self.r.smembers(key_pattern + ":icon"))
            weather.temp = self.r.get(key_pattern + ":temp")
            weather.temp_max = self.r.get(key_pattern + ":temp_max")
            weather.temp_min = self.r.get(key_pattern + ":temp_min")
            weather.pressure = self.r.get(key_pattern + ":pressure")
            weather.humidity = self.r.get(key_pattern + ":humidity")
            weather.clouds = self.r.get(key_pattern + ":clouds")
            weather.sunrise = self.r.get(key_pattern + ":sunrise")
            weather.sunset = self.r.get(key_pattern + ":sunset")
            weather.wind_speed = self.r.get(key_pattern + ":wind_speed")
            weather.last_time_update = self.r.get(key_pattern + ":last_time_update")
            weather.last_date_update = self.r.get(key_pattern + ":last_date_update")
            if self.r.exists("device:" + device_id + ":rules") == 1:
                rules_id = self.r.lrange("device:" + device_id + ":rules")
                for rule_id in rules_id:
                    rule_name = self.r.get("user:" + user_id + ":rule:" + rule_id + ":name")
                    weather.rules.append({"id": rule_id, "name": rule_name})
            return weather
        except Exception as error:
            print(repr(error))
            return "error"

    def get_device_slim(self, device_id):
        try:
            key_pattern = "device:" + device_id
            dto = Weather()
            dto.id = device_id
            dto.name = self.r.get(key_pattern + ":name")
            return dto
        except Exception as error:
            print(repr(error))
            return "error"

    def update_device(self, new_device):
        try:
            dto = Weather()
            dto.device_mapping(new_device)
            key_pattern = "device:" + dto.id
            self.r.set(key_pattern + ":name", dto.name)
        except Exception as error:
            print(repr(error))
            return "error"

    def set_location(self, user_id, location_name, country, lat, lon):
        try:
            self.check_unused_locations(user_id)
            self.r.set("user:" + user_id + ":location:name", location_name)
            key_pattern = "weather:location:" + location_name
            self.r.set(key_pattern + ":country", country)
            self.r.set(key_pattern + ":lat", lat)
            self.r.set(key_pattern + ":lon", lon)
            self.r.sadd("weather:location:names", location_name)
            self.update_weather(location_name)
            return "true"
        except Exception as error:
            print(repr(error))
            return "error"

    def check_unused_locations(self, user_id):
        try:
            if self.r.exists("user:" + user_id + ":location:name") == 1:
                old_location_name = self.r.get("user:" + user_id + ":location:name")
                self.r.set("user:" + user_id + ":location:name", "")
                all_users_location = set(self.r.scan("user:*:location:name"))
                if old_location_name not in all_users_location:
                    self.delete_weather(old_location_name)
        except Exception as error:
            print(repr(error))

    def get_location(self, user_id):
        try:
            location_name = self.r.get("user:" + user_id + ":location:name")
            key_pattern = "weather:location:" + location_name
            country = self.r.get(key_pattern + ":country")
            lat = self.r.get(key_pattern + ":lat")
            lon = self.r.get(key_pattern + ":lon")
            output = Location(location_name, country, lat, lon)
            return output
        except Exception as error:
            print(repr(error))
            return "error"

    def search_new_location(self, location_name):
        try:
            r = requests.get(self.api_location_url, params={'q': location_name, 'limit': 5, 'appid': self.api_key})
            data = r.json()
            return data
        except Exception as error:
            print(repr(error))
            return "error"

    def update_weather(self, location_name):
        try:
            key_pattern = "weather:" + location_name
            if self.r.exists(key_pattern + ":name") == 1:
                last_time_update_str = self.r.get(key_pattern + ":last_time_update")
                last_date_update_str = self.r.get(key_pattern + ":last_date_update")
                datetime_str = last_date_update_str + " " + last_time_update_str
                date_time_obj = datetime.strptime(datetime_str, '%d/%m/%Y %H:%M')
                delta_time = datetime.now() - date_time_obj
                if delta_time.total_seconds() > self.weather_refresh_cycle:
                    self.adapter_api_weather(location_name)
            else:
                self.adapter_api_weather(location_name)
        except Exception as error:
            print(repr(error))
            return "error"

    def adapter_api_weather(self, location_name):
        try:
            print("WEATHER API GET")
            location_key_pattern = "weather:location:" + location_name
            lat = self.r.get(location_key_pattern + ":lat")
            lon = self.r.get(location_key_pattern + ":lon")
            r = requests.get(self.api_weather_url,
                             params={'units': 'metric', 'lat': lat, 'lon': lon, 'appid': self.api_key})
            data = r.json()
            dto = WeatherResponse(DefaultMunch.fromDict(data))
            dto.name = location_name
            self.save_weather(dto)
        except Exception as error:
            print(repr(error))
            return "error"

    def save_weather(self, dto: WeatherResponse):
        key_pattern = "weather:" + dto.name
        self.r.set(key_pattern + ":name", dto.name)
        self.r.delete(key_pattern + ":icon")
        for i in range(0, len(dto.weather)):
            icon = list(dto.weather[i].icon)
            icon[-1] = "d"
            icon_d = "".join(icon)
            self.r.sadd(key_pattern + ":icon", icon_d)
        self.r.set(key_pattern + ":temp", str(dto.main.temp))
        self.r.set(key_pattern + ":temp_max", str(dto.main.temp_max))
        self.r.set(key_pattern + ":temp_min", str(dto.main.temp_min))
        self.r.set(key_pattern + ":pressure", str(dto.main.pressure))
        self.r.set(key_pattern + ":humidity", str(dto.main.humidity))
        self.r.set(key_pattern + ":clouds", str(dto.clouds.all))
        self.r.set(key_pattern + ":sunrise", str(dto.sys.sunrise))
        self.r.set(key_pattern + ":sunset", str(dto.sys.sunset))
        self.r.set(key_pattern + ":wind_speed", str(dto.wind.speed))
        self.r.set(key_pattern + ":last_time_update", datetime.now().strftime("%H:%M"))
        self.r.set(key_pattern + ":last_date_update", datetime.now().strftime("%d/%m/%Y"))

    def delete_weather(self, location_name):
        self.r.srem("weather:location:names", location_name)
        location_key_pattern = "weather:location:" + location_name
        self.r.delete(location_key_pattern + ":lat")
        self.r.delete(location_key_pattern + ":lon")
        self.r.delete(location_key_pattern + ":country")
        key_pattern = "weather:" + location_name
        if self.r.exists(key_pattern + ":name") == 1:
            self.r.delete(key_pattern + ":name")
            self.r.delete(key_pattern + ":icon")
            self.r.delete(key_pattern + ":temp")
            self.r.delete(key_pattern + ":temp_max")
            self.r.delete(key_pattern + ":temp_min")
            self.r.delete(key_pattern + ":pressure")
            self.r.delete(key_pattern + ":humidity")
            self.r.delete(key_pattern + ":clouds")
            self.r.delete(key_pattern + ":sunrise")
            self.r.delete(key_pattern + ":sunset")
            self.r.delete(key_pattern + ":wind_speed")
