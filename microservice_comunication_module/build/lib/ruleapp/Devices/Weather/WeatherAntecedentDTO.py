
class IconAntecedent(object):
    def __init__(self):
        self.icon_value = []
        self.check_icon = "false"
        self.icon_condition = "between"
        self.icon_start_value = []
        self.icon_evaluation = "false"


class TempAntecedent(object):
    def __init__(self):
        self.temp_value = ""
        self.temp_unit = "Celsius"
        self.check_temp = "false"
        self.temp_condition = "between"
        self.temp_start_value = "-10"
        self.temp_stop_value = "40"
        self.temp_evaluation = "false"


class PressureAntecedent(object):
    def __init__(self):
        self.pressure_value = ""
        self.pressure_unit = "hPa"
        self.check_pressure = "false"
        self.pressure_condition = "between"
        self.pressure_start_value = "960"
        self.pressure_stop_value = "1060"
        self.pressure_evaluation = "false"


class HumidityAntecedent(object):
    def __init__(self):
        self.humidity_value = ""
        self.humidity_unit = "%"
        self.check_humidity = "false"
        self.humidity_condition = "between"
        self.humidity_start_value = "0"
        self.humidity_stop_value = "100"
        self.humidity_evaluation = "false"


class CloudAntecedent(object):
    def __init__(self):
        self.clouds_value = ""
        self.clouds_unit = "%"
        self.check_clouds = "false"
        self.clouds_condition = "between"
        self.clouds_start_value = "0"
        self.clouds_stop_value = "100"
        self.cloud_evaluation = "false"


class TimeAntecedent(object):
    def __init__(self):
        self.time_value = ""
        self.sunrise = ""
        self.sunset = ""
        self.check_time = "false"
        self.time_condition = "between"
        self.time_start_value = "-"
        self.time_stop_value = "-"
        self.time_evaluation = "false"


class WindAntecedent(object):
    def __init__(self):
        self.wind_speed_value = ""
        self.wind_speed_unit = "meter/sec"
        self.check_wind_speed = "false"
        self.wind_speed_condition = "between"
        self.wind_speed_start_value = "0"
        self.wind_speed_stop_value = "30"
        self.wind_speed_evaluation = "false"


class WeatherAntecedent(object):
    def __init__(self):
        self.device_id = ""
        self.device_name = ""
        self.icon_value = []
        self.temp_value = ""
        self.temp_unit = "Celsius"
        self.pressure_value = ""
        self.pressure_unit = "hPa"
        self.humidity_value = ""
        self.humidity_unit = "%"
        self.clouds_value = ""
        self.clouds_unit = "%"
        self.sunrise = ""
        self.sunset = ""
        self.wind_speed_value = ""
        self.wind_speed_unit = "meter/sec"
        self.check_icon = "true"
        self.icon_condition = ""
        self.icon_start_value = []
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
        self.time_value = ""
        self.check_wind_speed = "true"
        self.wind_speed_condition = ""
        self.wind_speed_start_value = ""
        self.wind_speed_stop_value = ""
        self.icon_evaluation = "false"
        self.temp_evaluation = "false"
        self.pressure_evaluation = "false"
        self.humidity_evaluation = "false"
        self.cloud_evaluation = "false"
        self.time_evaluation = "false"
        self.wind_speed_evaluation = "false"
        self.evaluation = "false"

    def set_icon_antecedent(self, dto: IconAntecedent):
        self.check_icon = dto.check_icon
        self.icon_condition = dto.icon_condition
        self.icon_start_value = dto.icon_start_value
        self.icon_evaluation = dto.icon_evaluation
        self.icon_value = dto.icon_value

    def get_icon_antecedent(self):
        dto = IconAntecedent()
        dto.check_icon = self.check_icon
        dto.icon_condition = self.icon_condition
        dto.icon_start_value = self.icon_start_value
        dto.icon_evaluation = self.icon_evaluation
        dto.icon_value = self.icon_value
        return dto

    def set_temp_antecedent(self, dto: TempAntecedent):
        self.check_temp = dto.check_temp
        self.temp_condition = dto.temp_condition
        self.temp_start_value = dto.temp_start_value
        self.temp_stop_value = dto.temp_stop_value
        self.temp_evaluation = dto.temp_evaluation
        self.temp_value = dto.temp_value

    def get_temp_antecedent(self):
        dto = TempAntecedent()
        dto.check_temp = self.check_temp
        dto.temp_condition = self.temp_condition
        dto.temp_start_value = self.temp_start_value
        dto.temp_stop_value = self.temp_stop_value
        dto.temp_evaluation = self.temp_evaluation
        dto.temp_value = self.temp_value
        return dto

    def set_pressure_antecedent(self, dto: PressureAntecedent):
        self.check_pressure = dto.check_pressure
        self.pressure_condition = dto.pressure_condition
        self.pressure_start_value = dto.pressure_start_value
        self.pressure_stop_value = dto.pressure_stop_value
        self.pressure_evaluation = dto.pressure_evaluation
        self.pressure_value = dto.pressure_value

    def get_pressure_antecedent(self):
        dto = PressureAntecedent()
        dto.pressure_condition = self.pressure_condition
        dto.pressure_start_value = self.pressure_start_value
        dto.pressure_stop_value = self.pressure_stop_value
        dto.pressure_evaluation = self.pressure_evaluation
        dto.pressure_value = self.pressure_value
        return dto

    def set_humidity_antecedent(self, dto: HumidityAntecedent):
        self.check_humidity = dto.check_humidity
        self.humidity_condition = dto.humidity_condition
        self.humidity_start_value = dto.humidity_start_value
        self.humidity_stop_value = dto.humidity_stop_value
        self.humidity_evaluation = dto.humidity_evaluation
        self.humidity_value = dto.humidity_value

    def get_humidity_antecedent(self):
        dto = HumidityAntecedent()
        dto.check_humidity = self.check_humidity
        dto.humidity_condition = self.humidity_condition
        dto.humidity_start_value = self.humidity_start_value
        dto.humidity_stop_value = self.humidity_stop_value
        dto.humidity_evaluation = self.humidity_evaluation
        dto.humidity_value = self.humidity_value
        return dto

    def set_cloud_antecedent(self, dto: CloudAntecedent):
        self.check_clouds = dto.check_clouds
        self.clouds_condition = dto.clouds_condition
        self.clouds_start_value = dto.clouds_start_value
        self.clouds_stop_value = dto.clouds_stop_value
        self.cloud_evaluation = dto.cloud_evaluation
        self.clouds_value = dto.clouds_value

    def get_cloud_antecedent(self):
        dto = CloudAntecedent()
        dto.check_clouds = self.check_clouds
        dto.clouds_condition = self.clouds_condition
        dto.clouds_start_value = self.clouds_start_value
        dto.clouds_stop_value = self.clouds_stop_value
        dto.cloud_evaluation = self.cloud_evaluation
        dto.clouds_value = self.clouds_value
        return dto

    def set_time_antecedent(self, dto: TimeAntecedent):
        self.check_time = dto.check_time
        self.time_condition = dto.time_condition
        self.time_start_value = dto.time_start_value
        self.time_stop_value = dto.time_start_value
        self.time_evaluation = dto.time_evaluation
        self.sunrise = dto.sunrise
        self.sunset = dto.sunset
        self.time_value = dto.time_value

    def get_time_antecedent(self):
        dto = TimeAntecedent()
        dto.check_time = self.check_time
        dto.time_condition = self.time_condition
        dto.time_start_value = self.time_start_value
        dto.time_start_value = self.time_start_value
        dto.temp_evaluation = self.temp_evaluation
        dto.sunset = self.sunset
        dto.sunrise = self.sunrise
        dto.time_value = self.time_value
        return dto

    def set_wind_antecedent(self, dto: WindAntecedent):
        self.check_wind_speed = dto.check_wind_speed
        self.wind_speed_condition = dto.wind_speed_condition
        self.wind_speed_start_value = dto.wind_speed_start_value
        self.wind_speed_stop_value = dto.wind_speed_start_value
        self.wind_speed_evaluation = dto.wind_speed_evaluation
        self.wind_speed_value = dto.wind_speed_value

    def get_wind_antecedent(self):
        dto = WindAntecedent()
        dto.check_wind_speed = self.check_wind_speed
        dto.wind_speed_condition = self.wind_speed_condition
        dto.wind_speed_start_value = self.wind_speed_start_value
        dto.wind_speed_start_value = self.wind_speed_start_value
        dto.wind_speed_evaluation = self.wind_speed_evaluation
        dto.wind_speed_value = self.wind_speed_value
        return dto

    def antecedent_mapping(self, antecedent):
        self.device_id = antecedent["device_id"]
        self.device_name = antecedent["device_name"]
        self.check_icon = antecedent["check_icon"]
        self.icon_condition = antecedent["icon_condition"]
        self.icon_start_value = antecedent["icon_start_value"]
        self.check_temp = antecedent["check_temp"]
        self.temp_condition = antecedent["temp_condition"]
        self.temp_start_value = antecedent["temp_start_value"]
        self.temp_stop_value = antecedent["temp_stop_value"]
        self.check_pressure = antecedent["check_pressure"]
        self.pressure_condition = antecedent["pressure_condition"]
        self.pressure_start_value = antecedent["pressure_start_value"]
        self.pressure_stop_value = antecedent["pressure_stop_value"]
        self.check_humidity = antecedent["check_humidity"]
        self.humidity_condition = antecedent["humidity_condition"]
        self.humidity_start_value = antecedent["humidity_start_value"]
        self.humidity_stop_value = antecedent["humidity_stop_value"]
        self.check_clouds = antecedent["check_clouds"]
        self.clouds_condition = antecedent["clouds_condition"]
        self.clouds_start_value = antecedent["clouds_start_value"]
        self.clouds_stop_value = antecedent["clouds_stop_value"]
        self.check_time = antecedent["check_time"]
        self.time_condition = antecedent["time_condition"]
        self.time_start_value = antecedent["time_start_value"]
        self.time_stop_value = antecedent["time_stop_value"]
        self.check_wind_speed = antecedent["check_wind_speed"]
        self.wind_speed_condition = antecedent["wind_speed_condition"]
        self.wind_speed_start_value = antecedent["wind_speed_start_value"]
        self.wind_speed_stop_value = antecedent["wind_speed_stop_value"]

