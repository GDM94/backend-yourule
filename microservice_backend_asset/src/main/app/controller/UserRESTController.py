from flask import Blueprint
from ..services.UserServiceImpl import UserService
import json
from functools import wraps
from flask import request
from werkzeug.datastructures import ImmutableMultiDict
import jwt
from .configuration.config import read_config
from ruleapp.DBconnection.RedisConnectionImpl import RedisConnection

config = read_config()
redis = RedisConnection(config)
user = Blueprint('user', __name__)
secret_key = config.get("OAUTH", "token_key")
user_service = UserService(secret_key, redis, config)


def check_token(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if not request.headers.get('token'):
            return {'message': 'No token provided'}, 400
        try:
            params = request.args.to_dict()
            token_id = request.headers['token']
            claims = jwt.decode(token_id, secret_key, algorithms=["HS256"])
            params["user_id"] = claims["user_id"]
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
        profile_map = jwt.decode(access_token, secret_key, algorithms=["HS256"])
        output = user_service.user_login(profile_map)
        return output
    except Exception as error:
        print(repr(error))
        raise Exception()


@user.route('/registration', methods=["GET"])
def user_registration():
    try:
        access_token = request.args.get("access_token")
        profile_map = jwt.decode(access_token, secret_key, algorithms=["HS256"])
        output = user_service.user_registration(profile_map)
        return output
    except Exception as error:
        print(repr(error))
        raise Exception()


@user.route('/get/id/<user_name>', methods=["GET"])
def get_user_id(user_name):
    output = user_service.get_user_id(user_name)
    if output == "error":
        raise Exception()
    else:
        json_output = {"userId": output}
        return json.dumps(json_output)


@user.route('/set/location', methods=["POST"])
@check_token
def set_user_location():
    user_id = request.args.get("user_id")
    name = request.args.get("name")
    country = request.args.get("country")
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    output = user_service.set_user_location(user_id, name, country, lat, lon)
    if output == "error":
        raise Exception()
    else:
        return output


@user.route('/location', methods=["GET"])
@check_token
def get_user_location():
    user_id = request.args.get("user_id")
    output = user_service.get_user_location(user_id)
    if output == "error":
        raise Exception()
    else:
        return json.dumps(output, default=lambda o: o.__dict__, indent=4)


@user.route('/search/location/<name>', methods=["GET"])
@check_token
def search_new_location(name):
    output = user_service.search_new_location(name)
    if output == "error":
        raise Exception()
    else:
        return json.dumps(output)


@user.route('/get/weather', methods=["GET"])
def get_weather():
    # user_id = request.args.get("user_id")
    output = user_service.get_weather("1")
    if output == "error":
        raise Exception()
    else:
        return json.dumps(output)

