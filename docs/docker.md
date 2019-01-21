# Docker installation

## Requirements

To begin you need to have Docker compose. If you don't have it, follow [the official guide](https://docs.docker.com/compose/install/).

## Setup

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