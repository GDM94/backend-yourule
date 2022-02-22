class Weather(object):
    def __init__(self):
        self.id = "WEATHER-"
        self.name = "WEATHER"
        self.color = "green"
        self.expiration = "no"
        self.location_name = ""
        self.country = ""
        self.lat = ""
        self.lon = ""
        self.icon = []
        self.temp = ""
        self.temp_unit = "Celsius"
        self.temp_max = ""
        self.temp_min = ""
        self.pressure = ""
        self.pressure_unit = "hPa"
        self.humidity = ""
        self.humidity_unit = "%"
        self.clouds = ""
        self.clouds_unit = "%"
        self.sunrise = ""
        self.sunset = ""
        self.wind_speed = ""
        self.wind_speed_unit = "meter/sec"
        self.last_time_update = ""
        self.last_date_update = ""
        self.rules = []
        self.type = "sensor"

    def device_mapping(self, device):
        self.id = device["id"]
        self.name = device["name"]
