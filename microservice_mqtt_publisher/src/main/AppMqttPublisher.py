from flask import Flask
from flask_cors import CORS
from flask import request
from configuration.config import read_config
from controller.MQTTPublisher import Publisher
import random
import string

app = Flask(__name__)
CORS(app)

config = read_config()
client_id = 'publisher'.join(random.choices(string.ascii_letters + string.digits, k=8))
publisher = Publisher(client_id, config.get("MQTT", "broker"), config.get("MQTT", "port"))
publisher.start_connection()


@app.route('/mqtt/publish/<actuator>/<device_id>', methods=['POST'])
def publish(actuator, device_id):
    topic = actuator + "/" + device_id
    payload = request.get_json(force=True)
    msg = payload["message"]
    publisher.publish(topic, msg)
    return "true"


if __name__ == '__main__':
    app.run(host=config.get("FLASK", "host"), port=config.get("FLASK", "port"))
