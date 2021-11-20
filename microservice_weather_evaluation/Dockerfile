FROM python:3.9.2

RUN pip install redis;
RUN pip install pika;
RUN pip install ruleapp==0.10.1;
RUN pip install munch;
RUN pip install requests;

ADD ./src /backend/microservice_weather_evaluation/

WORKDIR /backend/microservice_weather_evaluation/main/

CMD [ "python", "-u", "AppWeatherEvaluation.py"]
