import json
from flask import request
from flask import Blueprint
from .UserRESTController import check_token
from flask import current_app as app
from flask import Response

rule = Blueprint('rule', __name__)


@rule.route('/id/<rule_id>', methods=['GET'])
@check_token
def get_rule_by_rule_id(rule_id):
    user_id = request.args.get("user_id")
    output = app.rule_service.get_rule_by_id(user_id, rule_id)
    if output == "error":
        raise Exception()
    else:
        return json.dumps(output, default=lambda o: o.__dict__, indent=4)


@rule.route('/antecedents', methods=['GET'])
@check_token
def get_antecedents_list():
    user_id = request.args.get("user_id")
    rule_id = request.args.get("rule_id")
    output = app.rule_service.get_rule_antecedents(user_id, rule_id)
    if output == "error":
        raise Exception()
    else:
        return json.dumps(output, default=lambda o: o.__dict__, indent=4)


@rule.route('/get/antecedent/<rule_id>/<device_id>', methods=['GET'])
@check_token
def get_antecedent(rule_id, device_id):
    user_id = request.args.get("user_id")
    output = app.rule_service.get_rule_antecedent(user_id, rule_id, device_id)
    if output == "error":
        raise Exception()
    else:
        return json.dumps(output, default=lambda o: o.__dict__, indent=4)


@rule.route('/consequents', methods=['GET'])
@check_token
def get_consequent_list():
    user_id = request.args.get("user_id")
    rule_id = request.args.get("rule_id")
    output = app.rule_service.get_rule_consequents(user_id, rule_id)
    if output == "error":
        raise Exception()
    else:
        return json.dumps(output, default=lambda o: o.__dict__, indent=4)


@rule.route('/get/consequent/<rule_id>/<device_id>', methods=['GET'])
@check_token
def get_consequent(rule_id, device_id):
    user_id = request.args.get("user_id")
    output = app.rule_service.get_rule_consequent(user_id, rule_id, device_id)
    if output == "error":
        raise Exception()
    else:
        return json.dumps(output, default=lambda o: o.__dict__, indent=4)


@rule.route('/create/<rule_name>', methods=['POST'])
@check_token
def create_rule(rule_name):
    user_id = request.args.get("user_id")
    output = app.rule_service.create_rule(user_id, rule_name)
    if output == "error":
        raise Exception()
    else:
        return json.dumps(output, default=lambda o: o.__dict__, indent=4)


@rule.route('/user', methods=['GET'])
@check_token
def get_rules_list():
    user_id = request.args.get("user_id")
    output = app.rule_service.get_user_rules(user_id)
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
    output = app.rule_service.update_rule_name(user_id, rule_id, rule_name)
    if output == "error":
        raise Exception()
    else:
        return output


@rule.route('/add/antecedent', methods=['POST'])
@check_token
def add_rule_antecedent():
    user_id = request.args.get("user_id")
    rule_id = request.args.get("rule_id")
    device_id = request.args.get("device_id")
    output = app.rule_service.add_rule_antecedent(user_id, rule_id, device_id)
    if output == "error":
        raise Exception()
    else:
        return json.dumps(output, default=lambda o: o.__dict__, indent=4)


@rule.route('/add/consequent', methods=['POST'])
@check_token
def add_rule_consequent():
    user_id = request.args.get("user_id")
    rule_id = request.args.get("rule_id")
    device_id = request.args.get("device_id")
    output = app.rule_service.add_rule_consequent(user_id, rule_id, device_id)
    if output == "error":
        raise Exception()
    else:
        return json.dumps(output, default=lambda o: o.__dict__, indent=4)


@rule.route('/update/antecedent/<rule_id>/<device_id>', methods=['POST'])
@check_token
def update_rule_antecedent(rule_id, device_id):
    user_id = request.args.get("user_id")
    payload = request.get_json()
    antecedent_json = json.loads(payload["ruleElement"])
    output = app.rule_service.update_rule_antecedent(user_id, rule_id, device_id, antecedent_json)
    if output == "error":
        raise Exception()
    else:
        return json.dumps(output, default=lambda o: o.__dict__, indent=4)


@rule.route('/update/consequent/<rule_id>/<device_id>', methods=['POST'])
@check_token
def update_rule_consequent(rule_id, device_id):
    user_id = request.args.get("user_id")
    payload = request.get_json()
    consequent_json = json.loads(payload["ruleElement"])
    output = app.rule_service.update_rule_consequent(user_id, rule_id, device_id, consequent_json)
    if output == "error":
        raise Exception()
    else:
        return json.dumps(output, default=lambda o: o.__dict__, indent=4)


@rule.route('/update/consequents/order', methods=['POST'])
@check_token
def update_rule_consequent_order():
    user_id = request.args.get("user_id")
    rule_id = request.args.get("rule_id")
    payload = request.get_json()
    consequents_id_list = json.loads(payload["data"])
    output = app.rule_service.update_rule_consequents_order(user_id, rule_id, consequents_id_list)
    if output == "error":
        raise Exception()
    else:
        return json.dumps(output, default=lambda o: o.__dict__, indent=4)


@rule.route("/delete/<rule_id>", methods=['DELETE'])
@check_token
def delete_rule(rule_id):
    user_id = request.args.get("user_id")
    output = app.rule_service.delete_rule(user_id, rule_id)
    if output == "error":
        raise Exception()
    else:
        return output


@rule.route('/delete/antecedent/<rule_id>/<device_id>', methods=["DELETE"])
@check_token
def delete_rule_antecedent(rule_id, device_id):
    user_id = request.args.get("user_id")
    output = app.rule_service.delete_antecedent(user_id, rule_id, device_id)
    if output == "error":
        raise Exception()
    else:
        return json.dumps(output, default=lambda o: o.__dict__, indent=4)


@rule.route('/delete/consequent/<rule_id>/<device_id>', methods=["DELETE"])
@check_token
def delete_rule_consequent(rule_id, device_id):
    user_id = request.args.get("user_id")
    output = app.rule_service.delete_consequent(user_id, rule_id, device_id)
    if output == "error":
        raise Exception()
    else:
        return json.dumps(output, default=lambda o: o.__dict__, indent=4)


@rule.route('/antecedent/evaluation', methods=['POST'])
def antecedent_evaluation():
    payload = request.get_json()
    user_id = str(payload["user_id"])
    device_id = str(payload["device_id"])
    measure = str(payload["measure"])
    rules = payload["rules"]
    output = app.functional_rule_service.antecedent_evaluation(user_id, device_id, measure, rules)
    return Response(json.dumps(output, default=lambda o: o.__dict__), mimetype='application/json')


@rule.route('/evaluation', methods=['POST'])
def rule_evaluation():
    payload = request.get_json()
    user_id = str(payload["user_id"])
    rules = payload["rules"]
    output = app.functional_rule_service.rule_evaluation(user_id, rules)
    return Response(json.dumps(output, default=lambda o: o.__dict__), mimetype='application/json')

