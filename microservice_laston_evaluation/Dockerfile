FROM python:3.9.2

RUN pip install requests;

ADD ./src /backend/microservice_laston_evaluation/

WORKDIR /backend/microservice_laston_evaluation/main/

CMD [ "python", "-u", "AppLastOnEvaluation.py"]
