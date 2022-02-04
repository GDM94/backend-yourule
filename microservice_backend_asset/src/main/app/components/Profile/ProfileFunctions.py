import jwt


class ProfileFunction(object):
    def __init__(self, redis, token_key):
        self.r = redis
        self.token_key = token_key

    def register(self, dto):
        try:
            output = "false"
            key_pattern = "profile:" + dto.email
            if self.r.exists(key_pattern + ":name") == 0:
                user_id = str(self.r.incr("profile:counter"))
                self.r.set(key_pattern + ":name", dto.name)
                self.r.set(key_pattern + ":password", dto.password)
                self.r.set(key_pattern + ":surname", dto.surname)
                self.r.set(key_pattern + ":user_id", user_id)
                self.r.set("user:" + user_id + ":email", dto.email)
                self.r.set("user:" + user_id + ":logged", "true")
                dto.user_id = user_id
                output = self.create_token(dto)
            return output
        except Exception as error:
            print(repr(error))
            return "error"

    def login(self, dto):
        try:
            key_pattern = "profile:" + dto.email
            output = "false"
            if self.r.exists(key_pattern + ":name") == 1:
                password = self.r.get(key_pattern + ":password")
                if password == dto.password:
                    dto.name = self.r.get(key_pattern + ":name")
                    dto.surname = self.r.get(key_pattern + ":surname")
                    dto.user_id = self.r.get(key_pattern + ":user_id")
                    self.r.set("user:" + dto.user_id + ":logged", "true")
                    output = self.create_token(dto)
            return output
        except Exception as error:
            print(repr(error))
            return "error"

    def logout(self, user_id):
        try:
            self.r.set("user:" + user_id + ":logged", "false")
            return "logout"
        except Exception as error:
            print(repr(error))
            return "error"

    def create_token(self, dto):
        payload = dto.__dict__
        return jwt.encode(payload, self.token_key, algorithm="HS256")
