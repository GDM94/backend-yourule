FROM python:3.9.2

RUN pip install redis;
RUN pip install paho-mqtt;
RUN pip install pika;
RUN pip install ruleapp==0.6.8;

ADD ./src /backend/microservice_consequent_evaluation/

WORKDIR /backend/microservice_consequent_evaluation/main/

CMD [ "python", "-u", "AppConsequentEvaluation.py"]
