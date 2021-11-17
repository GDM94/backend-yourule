from Devices.Weather.WeatherDTO import Weather


class TempAntecedent(object):
    def __init__(self):
        self.check_temp = "true"
        self.temp_condition = ""
        self.temp_start_value = ""
        self.temp_stop_value = ""


class PressureAntecedent(object):
    def __init__(self):
        self.check_pressure = "true"
        self.pressure_condition = ""
        self.pressure_start_value = ""
        self.pressure_stop_value = ""


class HumidityAntecedent(object):
    def __init__(self):
        self.check_humidity = "true"
        self.humidity_condition = ""
        self.humidity_start_value = ""
        self.humidity_stop_value = ""


class CloudAntecedent(object):
    def __init__(self):
        self.check_clouds = "true"
        self.clouds_condition = ""
        self.clouds_start_value = ""
        self.clouds_stop_value = ""


class TimeAntecedent(object):
    def __init__(self):
        self.check_time = "true"
        self.time_condition = ""
        self.time_start_value = ""
        self.time_stop_value = ""


class WindAntecedent(object):
    def __init__(self):
        self.check_wind_speed = "true"
        self.wind_speed_condition = ""
        self.wind_speed_start_value = ""
        self.wind_speed_stop_value = ""


class WeatherAntecedent(object):
    def __init__(self):
        self.device_id = ""
        self.device_name = ""
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
        self.check_icon = "true"
        self.icon_condition = ""
        self.icon_start_value = ""
        self.icon_stop_value = ""
        self.check_temp = "true"
        self.temp_condition = ""
        self.temp_start_value = ""
        self.temp_stop_value = ""
        self.check_pressure = "true"
        self.pressure_condition = ""
        self.pressure_start_value = ""
        self.pressure_stop_value = ""
        self.check_humidity = "true"
        self.humidity_condition = ""
        self.humidity_start_value = ""
        self.humidity_stop_value = ""
        self.check_clouds = "true"
        self.clouds_condition = ""
        self.clouds_start_value = ""
        self.clouds_stop_value = ""
        self.check_time = "true"
        self.time_condition = ""
        self.time_start_value = ""
        self.time_stop_value = ""
        self.check_wind_speed = "true"
        self.wind_speed_condition = ""
        self.wind_speed_start_value = ""
        self.wind_speed_stop_value = ""

    def set_device_weather(self, dto: Weather):
        self.device_id = dto.device_id
        self.device_name = dto.device_name
        self.icon = dto.icon
        self.temp = dto.temp
        self.temp_unit = dto.temp_unit
        self.temp_max = dto.temp_max
        self.temp_min = dto.temp_min
        self.pressure = dto.pressure
        self.pressure_unit = dto.pressure_unit
        self.humidity = dto.humidity
        self.humidity_unit = dto.humidity_unit
        self.clouds = dto.clouds
        self.clouds_unit = dto.clouds_unit
        self.sunrise = dto.sunrise
        self.sunset = dto.sunset
        self.wind_speed = dto.wind_speed
        self.wind_speed_unit = dto.wind_speed_unit

    def get_device_weather(self):
        dto = Weather()
        dto.device_id = self.device_id
        dto.device_name = self.device_name
        dto.icon = self.icon
        dto.temp = self.temp
        dto.temp_unit = self.temp_unit
        dto.temp_max = self.temp_max
        dto.temp_min = self.temp_min
        dto.pressure = self.pressure
        dto.pressure_unit = self.pressure_unit
        dto.humidity = self.humidity
        dto.humidity_unit = self.humidity_unit
        dto.clouds = self.clouds
        dto.clouds_unit = self.clouds_unit
        dto.sunrise = self.sunrise
        dto.sunset = self.sunset
        dto.wind_speed = self.wind_speed
        dto.wind_speed_unit = self.wind_speed_unit
        return dto

    def set_temp_antecedent(self, dto: TempAntecedent):
        self.check_temp = dto.check_temp
        self.temp_condition = dto.temp_condition
        self.temp_start_value = dto.temp_start_value
        self.temp_stop_value = dto.temp_stop_value

    def get_temp_antecedent(self):
        dto = TempAntecedent()
        dto.check_temp = self.check_temp
        dto.temp_condition = self.temp_condition
        dto.temp_start_value = self.temp_start_value
        dto.temp_stop_value = self.temp_stop_value
        return dto

    def set_pressure_antecedent(self, dto: PressureAntecedent):
        self.check_pressure = dto.check_pressure
        self.pressure_condition = dto.pressure_condition
        self.pressure_start_value = dto.pressure_start_value
        self.pressure_stop_value = dto.pressure_stop_value

    def get_pressure_antecedent(self):
        dto = PressureAntecedent()
        dto.pressure_condition = self.pressure_condition
        dto.pressure_start_value = self.pressure_start_value
        dto.pressure_stop_value = self.pressure_stop_value
        return dto

    def set_humidity_antecedent(self, dto: HumidityAntecedent):
        self.check_humidity = dto.check_humidity
        self.humidity_condition = dto.humidity_condition
        self.humidity_start_value = dto.humidity_start_value
        self.humidity_stop_value = dto.humidity_stop_value

    def get_humidity_antecedent(self):
        dto = HumidityAntecedent()
        dto.check_humidity = self.check_humidity
        dto.humidity_condition = self.humidity_condition
        dto.humidity_start_value = self.humidity_start_value
        dto.humidity_stop_value = self.humidity_stop_value
        return dto

    def set_cloud_antecedent(self, dto: CloudAntecedent):
        self.check_clouds = dto.check_clouds
        self.clouds_condition = dto.clouds_condition
        self.clouds_start_value = dto.clouds_start_value
        self.clouds_stop_value = dto.clouds_stop_value

    def get_cloud_antecedent(self):
        dto = CloudAntecedent()
        dto.check_clouds = self.check_clouds
        dto.clouds_condition = self.clouds_condition
        dto.clouds_start_value = self.clouds_start_value
        dto.clouds_stop_value = self.clouds_stop_value
        return dto

    def set_time_antecedent(self, dto: TimeAntecedent):
        self.check_time = dto.check_time
        self.time_condition = dto.time_condition
        self.time_start_value = dto.time_start_value
        self.time_stop_value = dto.time_start_value

    def get_time_antecedent(self):
        dto = TempAntecedent()
        dto.check_time = self.check_time
        dto.time_condition = self.time_condition
        dto.time_start_value = self.time_start_value
        dto.time_start_value = self.time_start_value
        return dto

    def set_wind_antecedent(self, dto: WindAntecedent):
        self.check_wind_speed = dto.check_wind_speed
        self.wind_speed_condition = dto.wind_speed_condition
        self.wind_speed_start_value = dto.wind_speed_start_value
        self.wind_speed_stop_value = dto.wind_speed_start_value

    def get_wind_antecedent(self):
        dto = WindAntecedent()
        dto.check_wind_speed = self.check_wind_speed
        dto.wind_speed_condition = self.wind_speed_condition
        dto.wind_speed_start_value = self.wind_speed_start_value
        dto.wind_speed_start_value = self.wind_speed_start_value
        return dto
