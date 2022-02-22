from ..components.Profile.ProfileDTO import ProfileDto
from ..components.Profile.ProfileFunctions import ProfileFunction
from flask import current_app as app


class UserService(object):
    def __init__(self, redis, config):
        self.secret_key = config.get("OAUTH", "token_key")
        self.r = redis
        token_key = config.get("OAUTH", "token_key")
        self.profile_functions = ProfileFunction(redis, token_key)

    def user_login(self, profile_map):
        try:
            profile = ProfileDto()
            profile.constructor_map(profile_map)
            output = self.profile_functions.login(profile)
            return output
        except Exception as error:
            print(repr(error))
            return "error"

    def user_registration(self, profile_map):
        try:
            profile = ProfileDto()
            profile.constructor_map(profile_map)
            output = self.profile_functions.register(profile)
            if output != "false" and output != "error":
                app.timer_functions.register(profile.user_id)
                app.alert_functions.register(profile.user_id, profile.email)
                app.weather_functions.register(profile.user_id)
            return output
        except Exception as error:
            print(repr(error))
            return "error"

    def user_logout(self, user_id):
        return self.profile_functions.logout(user_id)

    def get_user_id(self, user_name):
        try:
            output = self.r.get("user:name:" + user_name + ":id")
        except Exception as error:
            print(repr(error))
            return "error"
        else:
            return output

    def set_user_location(self, user_id, name, country, lat, lon):
        return app.weather_functions.set_location(user_id, name, country, lat, lon)

    def get_user_location(self, user_id):
        return app.weather_functions.get_location(user_id)

    def search_new_location(self, name):
        return app.weather_functions.search_new_location(name)
