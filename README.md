# LabAdmin

Labadmin is a Django application created to manage user rights to access the lab and the machines.

In this Readme you can follow the tutorial to set it up on a PC or Raspberry Pi. If you go in the ```Client``` folder you'll be able to access the different clients you can use with Labadmin 

## Installation

If you are going to deploy labAdmin from scratch on a new Django installation you have three choices:

- follow the [Tutorial](docs/tutorial.md)
- use the [Ansible role ](https://github.com/OfficineArduinoTorino/ansible-labadmin/)
- use Docker, follow the [Docker installation](docs/docker.md)

## Upgrade to a newer release

Before upgrading please read the [release notes](https://github.com/OfficineArduinoTorino/LabAdmin/releases) posted for each release on github.
They may contain changes you have to do on your Django project configuration.

First we are installing the latest release from github:

```
cd /var/www/labadmin/labadmin
sudo -H -u labadmin ../venv/bin/pip install <url of labadmin release from github.zip>
```

After that you'll have to do any project settings update as described in the release notes.

Then you have to execute any eventual data migration with the `migrate` command and update the static
files with `collectstatic`:

```
sudo -H -u labadmin ../venv/bin/python manage.py migrate
sudo -H -u labadmin ../venv/bin/python manage.py collectstatic
```

As a last step you have to restart the labadmin service to load the new code:

```
sudo service labadmin restart
```

## Settings

The optional MQTT integration has the following settings overridable in `settings.py`:

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
