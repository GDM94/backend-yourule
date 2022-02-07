from flask import Flask
from flask_cors import CORS
from app.controller.UserRESTController import user
from app.controller.DeviceRESTController import device
from app.controller.RuleRESTController import rule
from app.configuration.config import read_config
from app.DBconnection.RedisConnectionImpl import RedisConnection
from app.services.DeviceServiceImpl import DeviceService
from app.services.RuleServiceImpl import RuleService
from app.services.UserServiceImpl import UserService
from app.components.Devices.WaterLevel.WaterLevelFunctions import WaterLevelFunction
from app.components.Devices.Switch.SwitchFuntions import SwitchFunction
from app.components.Devices.Button.ButtonFunctions import ButtonFunction
from app.components.Devices.Timer.TimerFunctions import TimerFunction
from app.components.Devices.Alert.AlertFunctions import AlertFunction
from app.components.Devices.Weather.WeatherFunctions import WeatherFunction
from app.components.Devices.Photocell.PhotocellFunctions import PhotocellFunction
from app.components.Devices.Servo.ServoFunctions import ServoFunction
from app.components.Rule.RuleFunctions import RuleFunction
from app.components.Devices.Timer.TimerAntecedentFunctions import TimerAntecedentFunction
from app.components.Devices.Alert.AlertConsequentFunctions import AlertConsequentFunction
from app.components.Devices.WaterLevel.WaterLevelAntecedentFunctions import WaterLevelAntecedentFunction
from app.components.Devices.Switch.SwitchConsequentFunctions import SwitchConsequentFunction
from app.components.Devices.Button.ButtonAntecedentFunctions import ButtonAntecedentFunction
from app.components.Devices.Switch.SwitchAntecedentFunctions import SwitchAntecedentFunction
from app.components.Devices.Servo.ServoAntecedentFunctions import ServoAntecedentFunction
from app.components.Devices.Weather.WeatherAntecedentFunctions import WeatherAntecedentFunction
from app.components.Devices.Photocell.PhotocellAntecedentFunctions import PhotocellAntecedentFunction
from app.components.Devices.Servo.ServoConsequentFunctions import ServoConsequentFunction
from app.dataflow.DeviceEvaluationServiceImpl import DeviceEvaluationService
from app.dataflow.AntecedentEvaluationServiceImpl import AntecedentEvaluationService
from app.dataflow.RuleEvaluationServiceImpl import RuleEvaluationService
from app.dataflow.ConsequentEvaluationServiceImpl import ConsequentEvaluationService

config = read_config()
redis = RedisConnection(config)
host = config.get("FLASK", "host")
port = config.get("FLASK", "port")

app = Flask(__name__)
CORS(app)

app.device_service = DeviceService(redis, config)
app.rule_service = RuleService(redis, config)
app.user_service = UserService(redis, config)

app.switch_functions = SwitchFunction(redis)
app.waterlevel_functions = WaterLevelFunction(redis)
app.button_functions = ButtonFunction(redis)
app.timer_functions = TimerFunction(redis)
app.alert_functions = AlertFunction(redis)
app.weather_functions = WeatherFunction(redis, config)
app.photocell_functions = PhotocellFunction(redis)
app.servo_functions = ServoFunction(redis)
app.rule_functions = RuleFunction(redis)

app.timer_antecedent_functions = TimerAntecedentFunction(redis)
app.alert_consequent_functions = AlertConsequentFunction(redis)
app.waterlevel_antecedent_functions = WaterLevelAntecedentFunction(redis)
app.switch_consequent_functions = SwitchConsequentFunction(redis)
app.button_antecedent_functions = ButtonAntecedentFunction(redis)
app.switch_antecedent_functions = SwitchAntecedentFunction(redis)
app.servo_antecedent_functions = ServoAntecedentFunction(redis)
app.weather_antecedent_functions = WeatherAntecedentFunction(redis)
app.photocell_antecedent_functions = PhotocellAntecedentFunction(redis)
app.servo_consequent_functions = ServoConsequentFunction(redis)

app.device_evaluation_service = DeviceEvaluationService(redis, config)
app.antecedent_evaluation_service = AntecedentEvaluationService(redis)
app.rule_evaluation_service = RuleEvaluationService(redis)
app.consequent_evaluation_service = ConsequentEvaluationService(redis, config)


app.register_blueprint(rule, url_prefix='/rule')
app.register_blueprint(device, url_prefix='/device')
app.register_blueprint(user, url_prefix='/user')

if __name__ == '__main__':
    app.run(host=host, port=port)
