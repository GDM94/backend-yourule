from flask import Flask
from flask_cors import CORS
from app.controller.UserRESTController import user
from app.controller.DeviceRESTController import device
from app.controller.RuleRESTController import rule
from app.controller.configuration.config import read_config

# REST API
app = Flask(__name__)
CORS(app)
app.register_blueprint(rule, url_prefix='/rule')
app.register_blueprint(device, url_prefix='/device')
app.register_blueprint(user, url_prefix='/user')

# read configuration
config = read_config()
host = config.get("FLASK", "host")
port = config.get("FLASK", "port")

if __name__ == '__main__':
    app.run(host=host, port=port)
