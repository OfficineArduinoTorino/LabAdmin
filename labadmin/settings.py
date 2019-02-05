from django.conf import settings

from paho.mqtt.client import MQTTv311


BASE_MQTT_CONFIG = {
    'HOSTNAME': 'localhost',
    'PORT': 1883,
    'AUTH': None,
    'TLS': None,
    'PROTOCOL': MQTTv311,
    'TRANSPORT': 'tcp',
}
MQTT_CONFIG = {}


USER_MQTT_CONFIG = getattr(settings, 'LABADMIN_MQTT_CONFIG', {})

MQTT_CONFIG = BASE_MQTT_CONFIG.copy()
MQTT_CONFIG.update(USER_MQTT_CONFIG)
