FROM python:3.9.2

RUN pip install pika;
RUN pip install ruleapp==0.11.2;
RUN pip install requests;

ADD ./src /backend/microservice_antecedent_evaluation/

WORKDIR /backend/microservice_antecedent_evaluation/main/

CMD [ "python", "-u", "AppAntecedentEvaluation.py"]
