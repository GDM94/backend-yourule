FROM python:3.9.2

RUN pip install pyjwt;
RUN pip install -U flask-cors;
RUN pip install Flask;
RUN pip install redis;
RUN pip install paho-mqtt;
RUN pip install pika;
RUN pip install gunicorn;
RUN pip install requests;
RUN pip install ruleapp==0.6.3;


ADD ./src /backend/microservice_backend_asset/src/

WORKDIR /backend/microservice_backend_asset/src/main/

CMD ["gunicorn", "AppBackendAsset:app" ,"--workers=9", "--threads=5", "--timeout=120", "-b :5000"]
