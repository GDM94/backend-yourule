class TimerFunction(object):
    def __init__(self, redis):
        self.r = redis

    def register(self, timer_dto):
        if self.r.exists("device:" + timer_dto.device_id + ":name") == 0:
            key_pattern = "device:" + timer_dto.device_id
            self.r.set(key_pattern+":name", timer_dto.name)
