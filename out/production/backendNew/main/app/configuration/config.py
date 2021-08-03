import configparser
from os.path import dirname, join, abspath


def read_config():
    d = dirname(dirname(dirname(dirname(abspath(__file__)))))
    config_path = join(d, 'properties', 'app-config.ini')
    config = configparser.ConfigParser()
    config.read(config_path)
    return config
