FROM python:3.9.2

RUN pip install redis;
RUN pip install pika;

ADD ./src /backend/microservice_antecedent_evaluation/

WORKDIR /backend/microservice_antecedent_evaluation/main/

CMD [ "python", "-u", "AppAntecedentEvaluation.py"]
