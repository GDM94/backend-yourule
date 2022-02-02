from flask import Flask
from flask_cors import CORS
from flask import request
from configuration.config import read_config
from controller.RabbitMqClient import RabbitMQ
import random
import string
import json
from flask_mqtt import Mqtt

config = read_config()
client_id = 'device_endpoint'.join(random.choices(string.ascii_letters + string.digits, k=8))

app = Flask(__name__)
app.config['MQTT_CLIENT_ID'] = client_id
app.config['MQTT_BROKER_URL'] = config.get("MQTT", "broker")  # use the free broker from HIVEMQ
app.config['MQTT_BROKER_PORT'] = int(config.get("MQTT", "port"))  # default port for non-tls connection
app.config['MQTT_USERNAME'] = ''  # set the username here if you need authentication for the broker
app.config['MQTT_PASSWORD'] = ''  # set the password here if the broker demands authentication
app.config['MQTT_KEEPALIVE'] = 5  # set the time interval for sending a ping to the broker to 5 seconds
app.config['MQTT_TLS_ENABLED'] = False  # set TLS to disabled for testing purposes
CORS(app)

mqtt = Mqtt(app)

rabbitmq = RabbitMQ("device_endpoint", config)
rabbitmq.start_connection()


@app.route('/mqtt/publish/<actuator>/<device_id>', methods=['POST'])
def publish_mqtt(actuator, device_id):
    topic = actuator + "/" + device_id
    payload = request.get_json(force=True)
    msg = payload["message"]
    mqtt.publish(topic, msg)
    return "true"


@app.route('/rabbitmq/publish/<topic>', methods=['POST'])
def publish_rabbit_mq(topic):
    payload = request.get_json(force=True)
    rabbitmq.publish(topic, json.dumps(payload))
    return "true"


if __name__ == '__main__':
    app.run(host=config.get("FLASK", "host"), port=config.get("FLASK", "port"))
