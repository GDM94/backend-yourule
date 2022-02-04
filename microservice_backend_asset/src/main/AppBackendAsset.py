from flask import Flask
from flask_cors import CORS
from app.controller.UserRESTController import user
from app.controller.DeviceRESTController import device
from app.controller.RuleRESTController import rule
from app.configuration.config import read_config
from ruleapp.DBconnection.RedisConnectionImpl import RedisConnection
from app.services.DeviceServiceImpl import DeviceService
from app.services.RuleServiceImpl import RuleService
from app.services.UserServiceImpl import UserService
from app.services.DeviceFunctionalServiceImpl import DeviceFunctionalService

config = read_config()
redis = RedisConnection(config)
host = config.get("FLASK", "host")
port = config.get("FLASK", "port")

app = Flask(__name__)
CORS(app)

app.device_service = DeviceService(redis, config)
app.rule_service = RuleService(redis, config)
app.user_service = UserService(redis, config)
app.device_functional_service = DeviceFunctionalService(redis, config)

app.register_blueprint(rule, url_prefix='/rule')
app.register_blueprint(device, url_prefix='/device')
app.register_blueprint(user, url_prefix='/user')

if __name__ == '__main__':
    app.run(host=host, port=port)
