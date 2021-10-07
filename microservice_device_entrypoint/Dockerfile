FROM python:3.9.2

RUN pip install paho-mqtt;
RUN pip install pika;
RUN pip install redis;
RUN pip install ruleapp;

ADD ./src /backend/microservice_device_entrypoint/

WORKDIR /backend/microservice_device_entrypoint/main/

CMD [ "python", "-u", "AppDeviceEntryPoint.py"]