from flask import Blueprint
from ..services.UserServiceImpl import UserService
import json
from functools import wraps
from flask import request
from werkzeug.datastructures import ImmutableMultiDict
import jwt
from ...config import read_config
from ..services.RedisConnectionImpl import RedisConnection

config = read_config()
redis = RedisConnection(config)
user = Blueprint('user', __name__)
secret_key = config.get("OAUTH", "secret")
user_service = UserService(secret_key, redis)


def check_token(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if not request.headers.get('Authorization'):
            return {'message': 'No token provided'}, 400
        try:
            params = request.args.to_dict()
            token_id = request.headers['Authorization']
            claims = jwt.decode(token_id, secret_key, algorithms=["HS256"])
            params["user_id"] = claims["uid"]
            request.args = ImmutableMultiDict(params)
        except Exception as error:
            print(repr(error))
            return {'message': 'Invalid token provided.'}, 400
        else:
            return f(*args, **kwargs)
    return wrap


@user.route('/login', methods=["GET"])
def user_login():
    try:
        access_token = request.args.get("access_token")
        claims = jwt.decode(access_token, secret_key, algorithms=["HS256"])
        email = claims["email"]
        password = claims["password"]
        output = user_service.user_login(email, password)
    except Exception as error:
        print(repr(error))
        raise Exception()
    else:
        return json.dumps(output)


@user.route('/registration', methods=["GET"])
def user_registration():
    try:
        access_token = request.args.get("access_token")
        claims = jwt.decode(access_token, secret_key, algorithms=["HS256"])
        print(claims)
        email = claims["email"]
        password = claims["password"]
        name = claims["name"]
        surname = claims["surname"]
        output = user_service.user_registration(email, password, name, surname)
        print(output)
    except Exception as error:
        print(repr(error))
        raise Exception()
    else:
        return json.dumps(output)


@user.route('/get/id/<user_name>', methods=["GET"])
def get_user_id(user_name):
    output = user_service.get_user_id(user_name)
    if output == "error":
        raise Exception()
    else:
        json_output = {"userId": output}
        return json.dumps(json_output)


@user.route('/names', methods=["GET"])
def get_users_name():
    output = user_service.get_user_names()
    if output == "error":
        raise Exception()
    else:
        return json.dumps(output)


@user.route('/check/logged/<user_name>', methods=["GET"])
def get_user_logged(user_name):
    output = user_service.get_user_logged(user_name)
    if output == "error":
        raise Exception()
    else:
        return output


@user.route('/logout/<user_name>', methods=["POST"])
def user_logout(user_name):
    user_service.user_logout(user_name)
    return "logout"
