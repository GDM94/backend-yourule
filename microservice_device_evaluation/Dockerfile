FROM python:3.9.2

RUN pip install requests;
RUN pip install pika;

ADD ./src /backend/microservice_device_evaluation/

WORKDIR /backend/microservice_device_evaluation/main/

CMD [ "python", "-u", "AppDeviceEvaluation.py"]