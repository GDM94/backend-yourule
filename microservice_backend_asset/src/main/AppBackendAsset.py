from flask import Flask
from flask_cors import CORS
from os.path import dirname, join, abspath
import configparser
from app.controller.UserRESTController import user
from app.controller.DeviceRESTController import device
from app.controller.RuleRESTController import rule
import logging

# REST API
app = Flask(__name__)
CORS(app)
app.register_blueprint(rule, url_prefix='/rule')
app.register_blueprint(device, url_prefix='/device')
app.register_blueprint(user, url_prefix='/user')

# read configuration
d = dirname(dirname(abspath(__file__)))
config_path = join(d, 'properties', 'app-config.ini')
my_config = configparser.ConfigParser()
my_config.read(config_path)
HOST = my_config.get("FLASK", "host")
PORT = my_config.get("FLASK", "port")

if __name__ == '__main__':
    app.run(host=HOST, port=PORT)
