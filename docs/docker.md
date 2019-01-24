# Docker installation

## Requirements

To begin you need to have Docker compose. If you don't have it, follow [the official guide](https://docs.docker.com/compose/install/).

### RaspberryPi special

Install Docker following the "Install using the repository" guide https://docs.docker.com/install/linux/docker-ce/debian/

but use the special Raspbian repository

```
$ sudo add-apt-repository \
   "deb [arch=armhf] https://download.docker.com/linux/raspbian \
   $(lsb_release -cs) \
   stable"
```

Because you then need to install this specific Docker version:

```
sudo apt-get install docker-ce=18.06.1~ce~3-0~raspbian
```

Install docker-compose with pip

```
pip install docker-compose
```

and then you might need to add the local pip bin folder to your PATH. Append

```
export PATH=$PATH:~/.local/bin
```

to your .bashrc file.

## Setup

> If you are **NOT** running this on RaspberryPi check the `docker-compose.yml` and remove the special flag on MariaDB.

Build everything by running

`docker-compose build`

from the main folder of this repo.

(You might prepend `sudo` to all these commands, depends on your installation of `docker-compose`)

Migrate the database with

`docker-compose run web python manage.py migrate`

and then create the super user with

`docker-compose run web python manage.py createsuperuser`

finally, prepare the static assets with

`docker-compose run web python manage.py collectstatic`

## Run

Once the setup is done to start the project you need to run

`docker-compose up`

and then see your LabAdmin installation at [http://0.0.0.0:8000/labadmin/admin/](http://0.0.0.0:8000/labadmin/admin/)