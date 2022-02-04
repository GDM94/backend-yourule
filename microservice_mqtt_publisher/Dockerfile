FROM python:3.9.2

RUN pip install -U flask-cors;
RUN pip install Flask;
RUN pip install Flask-MQTT;
RUN pip install gunicorn;

ADD ./src /backend/microservice_mqtt_publisher/src/

WORKDIR /backend/microservice_mqtt_publisher/src/main/

CMD ["gunicorn", "AppMqttPublisher:app" ,"--workers=1", "--threads=1", "-b :5100"]