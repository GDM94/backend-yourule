FROM python:3.9.2

RUN pip install requests;
RUN pip install ruleapp==0.11.2;

ADD ./src /backend/microservice_timer_evaluation/

WORKDIR /backend/microservice_timer_evaluation/main/

CMD [ "python", "-u", "AppTimerEvaluation.py"]
