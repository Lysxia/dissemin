# coding: utf-8

### Security key ###
# This is used by django to generate various things (mainly for 
# authentication). Just pick a fairly random string and keep it
# secret.
SECRET_KEY = '40@!t4mmh7325-^wh+jo3teu^!yj3lfz5p%ok(8+7th8pg^hy1'

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'dissemin',
        'USER': 'dissemin',
        'PASSWORD': 'dissemin',
        'HOST': 'localhost'
    }
}

# Redis (if you use it)
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PASSWORD = ''

### Emailing settings ###
# These are used to send messages to the researchers.
# This is still a very experimental feature. We recommend you leave these
# settings as they are for now.
EMAIL_HOST = ''
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = True

### API keys ###
# These keys are used to communicate with various interfaces. See
# http://dissemin.readthedocs.org/en/latest/apikeys.html 

# RoMEO API KEY
# Used to fetch publisher policies. Get one at
# http://www.sherpa.ac.uk/romeo/apiregistry.php
ROMEO_API_KEY = None

# CORE API key
# Used to fetch full text availability. Get one at
# http://www.sherpa.ac.uk/romeo/apiregistry.php
CORE_API_KEY = None

