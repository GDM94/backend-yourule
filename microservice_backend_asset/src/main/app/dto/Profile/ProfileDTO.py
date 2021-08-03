
class ProfileDto(object):
    def __init__(self):
        self.email = ""
        self.name = ""
        self.surname = ""
        self.password = ""
        self.user_id = ""

    def constructor(self, email, name, surname, password):
        self.email = email
        self.name = name
        self.surname = surname
        self.password = password


