class UserFunction(object):
    def __init__(self, redis):
        self.r = redis

    def get_sensors(self, user_id):
        try:
            return self.r.lrange("user:" + user_id + ":sensors")
        except Exception as error:
            print(repr(error))
            return "error"

    def get_switches(self, user_id):
        try:
            return self.r.lrange("user:" + user_id + ":switches")
        except Exception as error:
            print(repr(error))
            return "error"

    def get_folders(self, user_id):
        try:
            return self.r.lrange("user:" + user_id + ":folders")
        except Exception as error:
            print(repr(error))
            return "error"

    def add_folder(self, user_id, folder_name):
        try:
            folder_id = str(self.r.incr("user:" + user_id + ":folder:counter"))
            self.r.rpush("user:" + user_id + ":folders", folder_id)
            self.r.set("user:" + user_id + ":folder:" + folder_id + ":name", folder_name)
            return "true"
        except Exception as error:
            print(repr(error))
            return "error"

    def delete_folder(self, user_id, folder_id):
        try:
            self.r.lrem("user:" + user_id + ":folders", folder_id)
            self.r.delete("user:" + user_id + ":folder:" + folder_id + ":name")
            return "true"
        except Exception as error:
            print(repr(error))
            return "error"

    def user_registration(self, user_id):
        return self.r.add_folder(user_id, "all rules")
