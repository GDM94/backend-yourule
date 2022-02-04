FROM python:3.9.2

RUN pip install requests;

ADD ./src /backend/microservice_timer_evaluation/

WORKDIR /backend/microservice_timer_evaluation/main/

CMD [ "python", "-u", "AppTimerEvaluation.py"]
