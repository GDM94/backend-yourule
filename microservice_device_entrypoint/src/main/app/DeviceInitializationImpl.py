class DeviceInitialization(object):
    def __init__(self, redis):
        self.r = redis

    def initialization(self, device_id, expiration):
        self.r.set("device:" + device_id + ":expiration", expiration)
