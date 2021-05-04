FROM redis:latest


COPY ./redis.conf /usr/local/etc/redis/redis.conf

EXPOSE 7002:6379

CMD [ "redis-server", "/usr/local/etc/redis/redis.conf" ]