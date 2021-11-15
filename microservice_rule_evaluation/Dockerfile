FROM python:3.9.2

RUN pip install redis;
RUN pip install pika;
RUN pip install ruleapp==0.7.6;

ADD ./src /backend/microservice_rule_evaluation/

WORKDIR /backend/microservice_rule_evaluation/main/

CMD [ "python", "-u", "AppRuleEvaluation.py"]
