# LabAdmin

Manage user rights to access the lab and the machines

## Quickstart

Install the labAdmin (`python3` and `virtualenv` required):

```
virtualenv -p python3 env
source env/bin/activate
python setup.py install
testSite/manage.py migrate
testSite/manage.py createsuperuser
```

Add it to the installed apps:

```
INSTALLED_APPS = [
    # ...
    'rest_framework',
    'oauth2_provider',
    'labAdmin',
]
```

Add labAdmin urls to your project urls:

```
urlpatterns = [
    # ...
    include(r'^labAdmin/', include('labAdmin.urls')),
]
```

Profit!

## Run Server

Running server for development:

`testSite/manage.py runserver 0.0.0.0:8000`

By default the server runs on `localhost:8000`

## Settings

The optional MQTT integration has the following settings:

```
LABADMIN_MQTT_CONFIG = {
    'HOSTNAME': 'localhost',
    'PORT': 1883,
    'AUTH': None,
    'TLS': None,
    'PROTOCOL': MQTTv311,
    'TRANSPORT': 'tcp',
}

# Should we publish on MQTT each entrance
LABADMIN_NOTIFY_MQTT_ENTRANCE = False

# The MQTT topic where to publish
LABADMIN_MQTT_ENTRANCE_TOPIC = 'labadmin/entrance'
```

See [Paho MQTT documentation](https://github.com/eclipse/paho.mqtt.python#single) for `LABADMIN_MQTT_CONFIG` values.
