FROM python:3.9.2

RUN pip install redis;
RUN pip install paho-mqtt;
RUN pip install pika;
RUN pip install ruleapp;

ADD ./src /backend/microservice_switch_sync/

WORKDIR /backend/microservice_switch_sync/main/

CMD [ "python", "-u", "AppSwitchSync.py"]
