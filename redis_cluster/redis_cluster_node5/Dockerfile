FROM arm32v7/redis:latest


COPY ./redis.conf /usr/local/etc/redis/redis.conf

EXPOSE 7005:6379

CMD [ "redis-server", "/usr/local/etc/redis/redis.conf" ]