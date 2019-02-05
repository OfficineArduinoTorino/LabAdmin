from .settings import MQTT_CONFIG
from paho.mqtt import publish


def mqtt_publish(topic, payload):
    config = {k.lower(): v for k, v in MQTT_CONFIG.items()}
    publish.single(topic, payload, **config)
