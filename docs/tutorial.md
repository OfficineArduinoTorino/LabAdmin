# Tutorial

Here's a tutorial to do a new install of *LabAdmin*. We are going to deploy *LabAdmin* on Ubuntu 16.04 LTS
using MySQL as database.

You need a checkout of this repository on your machine.

## Requirements

First we are going to install all requirements.
Please note that *mysql-server* will require a password for the root user that you'll need later.

```
sudo apt install build-essential python3 python3-dev libjpeg-dev libmysqlclient-dev git mysql-server nginx postfix libsasl2-2 libsasl2-modules python3-pip python3-venv sasl2-bin
sudo apt-get clean
```

### Mysql

In order to setup the mysql database we need to enter the mysql shell, youl'll be asked the root user password:

```
mysql -u root -p
```

From inside the shell we'll create the db, the user and grant the needed perms, please use a different password than the one below:

```
create database labadmin;
# please use a different password
CREATE USER 'labadmin'@'localhost' IDENTIFIED BY 'apasswordforlabadmin';
GRANT ALL PRIVILEGES ON labadmin.* TO 'labadmin'@'localhost';
FLUSH PRIVILEGES;
```

### Postfix

Postfix is needed for sending email, but it won't sending email on its own. Postfix will only relay the email to another SMTP server you need to have an account on.
When installing Postfix you'll be asked how to configure it, please select *Satellite System*. Then use the provided defaults for the other configuration questions.

Once the installation is done we need to tune some parameters in its config file */etc/postfix/main.cf*:

```
# smtp server address and port we'll use as relay
relayhost = [smtp.smtpserver]:port
```

And just copy bunch of options:

```
smtp_use_tls = yes
smtp_sasl_auth_enable = yes
smtp_sasl_password_maps = hash:/etc/postfix/sasl/sasl_passwd
smtp_sasl_security_options = noanonymous
smtp_sasl_tls_security_options = noanonymous
```

Then we need to create the credentials for the relay SMTP server in a file called */etc/postfix/sasl/sasl_passwd*:

```
[smtp.smtpserver] username:password
```

Execute the following commands to inizialize the credentials and set proper permissions:

```
sudo postmap /etc/postfix/sasl/sasl_passwd
chown -R root:postfix /etc/postfix/sasl
chmod 750 /etc/postfix/sasl
chmod 640 /etc/postfix/sasl/sasl_passwd*
```

Finally restart Postfix with the new settings:

```
sudo service postfix restart
```

## LabAdmin

Then we need to create a user that will run the *LabAdmin* application:

```
sudo useradd -M labadmin
sudo mkdir /var/www/labadmin
sudo chown labadmin /var/www/labadmin
cd /var/www/labadmin
```

Then we'll switch *labadmin* user for the next commands until further notice:

```
sudo su labadmin
```

We'll switch to a more comfortable shell:

```
bash
```

Now as the *labadmin* user we can setup the *LabAdmin* instance:

```
python3 -m venv venv
. ./venv/bin/activate
pip install --upgrade pip
pip install Django~=1.10 Pillow django-cors-middleware django-oauth-toolkit==0.10.0 djangorestframework mysqlclient paho-mqtt gunicorn
pip install https://github.com/OfficineArduinoTorino/LabAdmin/archive/v0.4.0.zip

mkdir bin
echo "#!/bin/sh" > bin/labadmin
echo ". /var/www/labadmin/venv/bin/activate" >> bin/labadmin
echo "gunicorn -w 2 -b 127.0.0.1:8888 labadmin.wsgi" >> bin/labadmin
chmod +x bin/labadmin
```

Then we are creating a django project:

```
django-admin startproject labadmin
mkdir labadmin/uploads labadmin/static
cd labadmin
python manage.py collectstatic
cd -
```

It's time to configure *labadmin/labadmin/settings.py*.

We need to add the needed apps:

```
INSTALLED_APPS = [
    # ...
    'django.contrib.sites',
    'rest_framework',
    'oauth2_provider',
    'corsheaders',
    'versatileimagefield',
    'labadmin',
]
```

And put the *CorsMiddleware* just before the *CommonMiddleware*:

```
MIDDLEWARE_CLASSES = [
    # ...
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    # ...
]
```

Then we need to setup the path for uploaded files, various urls and how long registration links are valid:

```
MEDIA_ROOT = '/var/www/labadmin/labadmin/uploads/'
STATIC_ROOT = '/var/www/labadmin/labadmin/static/'
STATIC_URL = '/labadmin/static/'
LOGIN_URL = '/labadmin/accounts/login/'
LOGIN_REDIRECT_URL = 'labadmin-user-profile'

# how many days the registration link will be valid
ACCOUNT_ACTIVATION_DAYS = 2

# id of default django.contrib.site.models.Site
SITE_ID = 1
```

You also need to update these settings dependings on your environment:

```
# See https://docs.djangoproject.com/en/1.10/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'labadmin',
        'USER': 'labadmin',
        'PASSWORD': 'apasswordforlabadmin',
        'HOST': '/var/run/mysqld/mysqld.sock',
    }
}

# these depends on where the machine is
LANGUAGE_CODE = 'it-it'
TIME_ZONE = 'Europe/Rome'

# email will be sent with this address in the from field
DEFAULT_FROM_EMAIL = 'myemail@mydomain.com'
```

We are done with django *settings.py*, it's time to add to *labadmin/labadmin/urls.py*:

```
from django.conf.urls import url, include
from django.contrib.auth import views as auth_views


labadminpatterns = [
    url(r'admin/', admin.site.urls),
    url(r'^labadmin/', include('labadmin.urls')),

    url(r'^accounts/login/$', auth_views.login, {'template_name': 'labadmin/login.html'}, name='login'),
    url(r'^accounts/logout/$', auth_views.logout, name='logout'),
    url(r'^accounts/password_reset/$', auth_views.password_reset, name='password_reset'),
    url(r'^accounts/password_reset/done/$', auth_views.password_reset_done, name='password_reset_done'),
    url(r'^accounts/reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', auth_views.password_reset_confirm, name='password_reset_confirm'),
    url(r'^accounts/reset/done/$', auth_views.password_reset_complete, name='password_reset_complete'),
    url(r'^accounts/', include('registration.backends.hmac.urls')),
]

urlpatterns = [
    url(r'^labadmin/', include(labadminpatterns)),
]
```

Now that our Django project is configured we can create the database tables and an admin user:

```
cd labadmin/labadmin
./manage.py migrate
./manage.py createsuperuser
```

We are going to remove the shell for the labadmin user. Remember to exit from the 
*labadmin* shell first and then type:

```
sudo usermod -s /bin/false labadmin
```

Finally we are telling the system how to load the application at startup.
Create */etc/systemd/system/labadmin.service* with this content:

```
[Unit]
Description=labadmin
Requires=network.target
After=network.target

[Service]
User=labadmin
WorkingDirectory=/var/www/labadmin/labadmin

ExecStart=/var/www/labadmin/bin/labadmin

[Install]
WantedBy=multi-user.target
```

Now we need to setup nginx to proxy for *LabAdmin*. 
Create */etc/nginx/conf.d/labadmin.conf* with this content:

```
upstream backenddjango {
    server 127.0.0.1:8888;
}

server {
    location /labadmin/static {
        alias /var/www/labadmin/labadmin/static;
    }
    location /labadmin {
        proxy_pass http://backenddjango;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $http_host;

        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forward-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forward-Proto http;
        proxy_set_header X-Nginx-Proxy true;

        proxy_redirect off;
    }
}
```

Then we need to restart nginx:

```
sudo service nginx configtest
sudo service nginx reload
```

Now *LabAdmin* admin interface should be reachable at your server ip [*/labadmin/admin*](http://127.0.0.1/labadmin/admin) path.
Log in the *LabAdmin* admin and update your *Site* domain (an ip address is fine too) and name to match the address it would reachable from outside.
