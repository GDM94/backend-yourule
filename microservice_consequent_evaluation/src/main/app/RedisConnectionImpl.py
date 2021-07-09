import redis


class RedisConnection(object):
    def __init__(self, config):
        host = config.get("REDIS", "host")
        port = config.get("REDIS", "port")
        self.expiration = config.get("REDIS", "expiration")
        self.r = redis.Redis(host=host, port=port, decode_responses=True)

    def set(self, key, value):
        self.r.set(key, value)

    def get(self, key):
        return self.r.get(key)

    def exists(self, key):
        return self.r.exists(key)

    def setex(self, key, value):
        self.r.setex(key, self.expiration, value)

    def smembers(self, key):
        return self.r.smembers(key)

    def lrange(self, key):
        return self.r.lrange(key, 0, -1)

    def scan(self, key):
        return self.r.scan(0, key, 1000)[1]
