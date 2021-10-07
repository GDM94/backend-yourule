from flask import Blueprint
from flask import request
from ..services.DeviceServiceImpl import DeviceService
import json
from .MQTTSubscriber import Subscriber
from .UserRESTController import check_token
from .RabbitMqClient import RabbitMQ
import random
import string
from .configuration.config import read_config
from ruleapp.DBconnection.RedisConnectionImpl import RedisConnection

config = read_config()
redis = RedisConnection(config)
device = Blueprint('device', __name__)
random_client_id = 'backend_device'.join(random.choices(string.ascii_letters + string.digits, k=8))
mqtt_client = Subscriber(random_client_id)
mqtt_client.start_connection()
rabbitmq = RabbitMQ("backend_device", config)
rabbitmq.start_connection()
device_service = DeviceService(mqtt_client, rabbitmq, redis, config)


@device.route('/get/<device_id>', methods=['GET'])
@check_token
def get_device(device_id):
    output = device_service.get_device(device_id)
    if output == "error":
        raise Exception()
    else:
        return json.dumps(output)


@device.route('/register', methods=['POST'])
@check_token
def device_registration():
    user_id = request.args.get("user_id")
    device_id = request.args.get("device_id")
    output = device_service.device_registration(user_id, device_id)
    if output == "error":
        raise Exception()
    else:
        return output


@device.route('/get/antecedents', methods=['GET'])
@check_token
def get_all_antecedents():
    user_id = request.args.get("user_id")
    output = device_service.get_all_sensors(user_id)
    if output == "error":
        raise Exception()
    else:
        return json.dumps(output, default=lambda o: o.__dict__, indent=4)


@device.route('/get/consequents', methods=['GET'])
@check_token
def get_all_consequents():
    user_id = request.args.get("user_id")
    output = device_service.get_all_switches(user_id)
    if output == "error":
        raise Exception()
    else:
        return json.dumps(output, default=lambda o: o.__dict__, indent=4)


@device.route('/delete/<device_id>', methods=['DELETE'])
@check_token
def delete_device(device_id):
    user_id = request.args.get("user_id")
    output = device_service.delete_device(user_id, device_id)
    if output == "error":
        raise Exception()
    else:
        return output


@device.route('/update/<device_id>', methods=['POST'])
@check_token
def device_update(device_id):
    payload = request.get_json()
    new_device = json.loads(payload)
    output = device_service.device_update(device_id, new_device)
    if output == "error":
        raise Exception()
    else:
        return output


@device.route('/consequent/automatic', methods=['POST'])
@check_token
def set_consequent_automatic():
    device_id = request.args.get("device_id")
    automatic = request.args.get("automatic")
    user_id = request.args.get("user_id")
    output = device_service.set_consequent_automatic(user_id, device_id, automatic)
    if output == "error":
        raise Exception()
    else:
        return json.dumps(output, default=lambda o: o.__dict__, indent=4)


@device.route('/consequent/manual', methods=['POST'])
@check_token
def set_consequent_manual_measure():
    device_id = request.args.get("device_id")
    manual_measure = request.args.get("manual_measure")
    output = device_service.set_consequent_manual_measure(device_id, manual_measure)
    if output == "error":
        raise Exception()
    else:
        return output


@device.route('/alert/add/', methods=['POST'])
@check_token
def add_alert_email():
    user_id = request.args.get("user_id")
    output = device_service.add_alert_email(user_id)
    if output == "error":
        raise Exception()
    else:
        return output


@device.route('/alert/modify/<email>/<idx>', methods=['POST'])
@check_token
def modify_alert_email(email, idx):
    user_id = request.args.get("user_id")
    output = device_service.modify_alert_email(user_id, email, idx)
    if output == "error":
        raise Exception()
    else:
        return output


@device.route('/alert/delete/<idx>', methods=['DELETE'])
@check_token
def delete_alert_email(idx):
    user_id = request.args.get("user_id")
    output = device_service.delete_alert_email(user_id, int(idx))
    if output == "error":
        raise Exception()
    else:
        return output
