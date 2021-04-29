FROM rabbitmq:latest

RUN rabbitmq-plugins enable --offline rabbitmq_management

COPY ./rabbitmq.conf /etc/rabbitmq/rabbitmq.conf
COPY ./definitions.json /etc/rabbitmq/definitions.json

EXPOSE 15672:15672
EXPOSE 5672:5672



