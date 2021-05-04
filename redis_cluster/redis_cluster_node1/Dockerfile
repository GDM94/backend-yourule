FROM redis:latest


COPY ./redis.conf /usr/local/etc/redis/redis.conf

EXPOSE 7001:6379

CMD [ "redis-server", "/usr/local/etc/redis/redis.conf" ]