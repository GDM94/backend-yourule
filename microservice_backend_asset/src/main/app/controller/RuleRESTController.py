import json
from flask import request
from flask import Blueprint
from ..dto.AntecedentDTO import Antecedent
from ..dto.ConsequentDTO import Consequent
from .MQTTSubscriber import Subscriber
from ..services.RuleServiceImpl import RuleService
from .UserRESTController import check_token
from .RabbitMqClient import RabbitMQ
import random
import string

rule = Blueprint('rule', __name__)
random_client_id = 'backend_rule'.join(random.choices(string.ascii_letters + string.digits, k=8))
mqtt_client = Subscriber(random_client_id)
mqtt_client.start_connection()
rabbitmq = RabbitMQ("backend_rule")
rabbitmq.start_connection()
rule_service = RuleService(mqtt_client, rabbitmq)


@rule.route('/device/<device_id>', methods=['GET'])
@check_token
def get_rules_id_by_device_id(device_id):
    user_id = request.args.get("user_id")
    output = rule_service.get_device_rules(user_id, device_id)
    if output == "error":
        raise Exception()
    else:
        json_output = {"rules": output}
        return json.dumps(json_output)


@rule.route('/id/<rule_id>', methods=['GET'])
@check_token
def get_rule_by_rule_id(rule_id):
    user_id = request.args.get("user_id")
    output = rule_service.get_rule_by_id(user_id, rule_id)
    if output == "error":
        raise Exception()
    else:
        return json.dumps(output, default=lambda o: o.__dict__, indent=4)


@rule.route("/delete/<rule_id>", methods=['DELETE'])
@check_token
def delete_rule_by_rule_id(rule_id):
    user_id = request.args.get("user_id")
    output = rule_service.delete_rule(user_id, rule_id)
    if output == "error":
        raise Exception()
    else:
        return output


@rule.route('/create/<rule_name>', methods=['POST'])
@check_token
def create_rule(rule_name):
    user_id = request.args.get("user_id")
    output = rule_service.create_new_rule(user_id, rule_name)
    if output == "error":
        raise Exception()
    else:
        return output


@rule.route('/user', methods=['GET'])
@check_token
def get_rules_by_user_id():
    user_id = request.args.get("user_id")
    output = rule_service.get_user_rules(user_id)
    if output == "error":
        raise Exception()
    else:
        return json.dumps(output, default=lambda o: o.__dict__, indent=4)


@rule.route('/set/name', methods=['POST'])
@check_token
def set_rule_name():
    user_id = request.args.get("user_id")
    rule_id = request.args.get("rule_id")
    rule_name = request.args.get("rule_name")
    output = rule_service.set_new_name(user_id, rule_id, rule_name)
    if output == "error":
        raise Exception()
    else:
        return output


@rule.route('/set', methods=['POST'])
@check_token
def set_rule():
    user_id = request.args.get("user_id")
    payload = request.get_json()
    rule_body = json.loads(payload["rule_json"])
    output = rule_service.set_rule(user_id, rule_body)
    if output == "error":
        raise Exception()
    else:
        return output


@rule.route('/set/antecedent', methods=['POST'])
@check_token
def set_rule_antecedent():
    user_id = request.args.get("user_id")
    rule_id = request.args.get("rule_id")
    device_id = request.args.get("device_id")
    start_value = request.args.get("start_value")
    stop_value = request.args.get("stop_value")
    condition = request.args.get("condition")
    measure = request.args.get("measure")
    antecedent = Antecedent(device_id, "", start_value, stop_value, condition, "false", measure)
    output = rule_service.set_new_antecedent(user_id, rule_id, antecedent)
    if output == "error":
        raise Exception()
    else:
        return output


@rule.route('/set/consequent', methods=['POST'])
@check_token
def set_rule_consequent():
    user_id = request.args.get("user_id")
    rule_id = request.args.get("rule_id")
    device_id = request.args.get("device_id")
    consequent = Consequent(device_id, "", "on", "off")
    output = rule_service.set_new_consequent(user_id, rule_id, consequent)
    if output == "error":
        raise Exception()
    else:
        return output


@rule.route('/delete/antecedent/<rule_id>/<device_id>', methods=["DELETE"])
@check_token
def delete_rule_antecedent(rule_id, device_id):
    user_id = request.args.get("user_id")
    output = rule_service.delete_antecedent(user_id, rule_id, device_id)
    if output == "error":
        raise Exception()
    else:
        return output


@rule.route('/delete/consequent/<rule_id>/<device_id>', methods=["DELETE"])
@check_token
def delete_rule_consequent(rule_id, device_id):
    user_id = request.args.get("user_id")
    output = rule_service.delete_consequent(user_id, rule_id, device_id)
    if output == "error":
        raise Exception()
    else:
        return output
