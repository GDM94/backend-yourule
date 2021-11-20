FROM python:3.9.2

RUN pip install redis;
RUN pip install pika;
RUN pip install ruleapp==0.10.1;

ADD ./src /backend/microservice_timer_evaluation/

WORKDIR /backend/microservice_timer_evaluation/main/

CMD [ "python", "-u", "AppTimerEvaluation.py"]
