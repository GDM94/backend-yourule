from flask import Blueprint
from flask import request
from ..services.DeviceServiceImpl import DeviceService
import json
from .MQTTSubscriber import Subscriber
from .UserRESTController import check_token
from .RabbitMqClient import RabbitMQ
import random
import string

device = Blueprint('device', __name__)
random_client_id = 'backend_device'.join(random.choices(string.ascii_letters + string.digits, k=8))
mqtt_client = Subscriber(random_client_id)
mqtt_client.start_connection()
rabbitmq = RabbitMQ("backend_device")
rabbitmq.start_connection()
device_service = DeviceService(mqtt_client, rabbitmq)


@device.route('/register', methods=['POST'])
@check_token
def device_registration():
    user_id = request.args.get("user_id")
    device_id = request.args.get("device_id")
    device_name = request.args.get("device_name")
    output = device_service.device_registration(user_id, device_id, device_name)
    if output == "error":
        raise Exception()
    else:
        return output


@device.route('/setting/<device_id>/<max_measure>/<error>', methods=['POST'])
@check_token
def device_update_setting(device_id, max_measure, error):
    output = device_service.device_update_setting(device_id, max_measure, error)
    if output == "error":
        raise Exception()
    else:
        return output


@device.route('/get/antecedents', methods=['GET'])
@check_token
def get_antecedent_by_user():
    user_id = request.args.get("user_id")
    output = device_service.get_user_antecedent_list(user_id)
    if output == "error":
        raise Exception()
    else:
        return json.dumps(output, default=lambda o: o.__dict__, indent=4)


@device.route('/get/consequents', methods=['GET'])
@check_token
def get_consequent_by_user():
    user_id = request.args.get("user_id")
    print(user_id)
    output = device_service.get_user_consequent_list(user_id)
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


@device.route('/update', methods=['POST'])
@check_token
def device_update():
    device_id = request.args.get("device_id")
    device_name = request.args.get("device_name")
    max_measure = request.args.get("setting")
    error = request.args.get("error")
    output = device_service.device_update(device_id, device_name, max_measure, error)
    if output == "error":
        raise Exception()
    else:
        return output


@device.route('/measure/<device_id>', methods=['GET'])
@check_token
def get_device_measure(device_id):
    output = device_service.get_device_measure(device_id)
    if output == "error":
        raise Exception()
    else:
        return output


@device.route('/antecedent/id/<device_id>', methods=['GET'])
@check_token
def get_antecedent_by_id(device_id):
    user_id = request.args.get("user_id")
    output = device_service.get_antecedent_device(user_id, device_id)
    if output == "error":
        raise Exception()
    else:
        return json.dumps(output, default=lambda o: o.__dict__, indent=4)


@device.route('/consequent/id/<device_id>', methods=['GET'])
@check_token
def get_consequent_by_id(device_id):
    user_id = request.args.get("user_id")
    output = device_service.get_consequent_device(user_id, device_id)
    if output == "error":
        raise Exception()
    else:
        return json.dumps(output, default=lambda o: o.__dict__, indent=4)


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


@device.route('/id/all', methods=['GET'])
@check_token
def get_all_devices_id():
    output = device_service.get_all_devices_id()
    if output == "error":
        raise Exception()
    else:
        return json.dumps(output)


@device.route('/alert/add/<email>', methods=['POST'])
@check_token
def add_alert_email(email):
    user_id = request.args.get("user_id")
    output = device_service.add_alert_email(user_id, email)
    if output == "error":
        raise Exception()
    else:
        return output


@device.route('/alert/delete/<email>', methods=['DELETE'])
@check_token
def delete_alert_email(email):
    user_id = request.args.get("user_id")
    output = device_service.delete_alert_email(user_id, email)
    if output == "error":
        raise Exception()
    else:
        return output
