from typing import List


class Clouds:
    all: int

    def __init__(self, percentage: int) -> None:
        self.all = percentage


class Coord:
    lon: float
    lat: float

    def __init__(self, lon: float, lat: float) -> None:
        self.lon = lon
        self.lat = lat


class Main:
    temp: float
    feels_like: float
    temp_min: float
    temp_max: float
    pressure: int
    humidity: int

    def __init__(self, temp: float, feels_like: float, temp_min: float, temp_max: float, pressure: int,
                 humidity: int) -> None:
        self.temp = temp
        self.feels_like = feels_like
        self.temp_min = temp_min
        self.temp_max = temp_max
        self.pressure = pressure
        self.humidity = humidity


class Sys:
    type: int
    id: int
    message: float
    country: str
    sunrise: int
    sunset: int

    def __init__(self, type_sys: int, id_sys: int, message: float, country: str, sunrise: int, sunset: int) -> None:
        self.type = type_sys
        self.id = id_sys
        self.message = message
        self.country = country
        self.sunrise = sunrise
        self.sunset = sunset


class Weather:
    id: int
    main: str
    description: str
    icon: str

    def __init__(self, id_weather: int, main: str, description: str, icon: str) -> None:
        self.id = id_weather
        self.main = main
        self.description = description
        self.icon = icon


class Wind:
    speed: float
    deg: int

    def __init__(self, speed: float, deg: int) -> None:
        self.speed = speed
        self.deg = deg


class Struct:
    coord: Coord
    weather: List[Weather]
    base: str
    main: Main
    visibility: int
    wind: Wind
    clouds: Clouds
    dt: int
    sys: Sys
    timezone: int
    id: int
    name: str
    cod: int

    def __init__(self, x) -> None:
        self.coord = x.coord
        self.weather = x.weather
        self.base = x.base
        self.main = x.main
        self.visibility = x.visibility
        self.wind = x.wind
        self.clouds = x.clouds
        self.dt = x.dt
        self.sys = x.sys
        self.timezone = x.timezone
        self.id = x.id_obj
        self.name = x.name
        self.cod = x.cod
