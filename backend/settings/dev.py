from .base import *

SECRET_KEY = 'h33=$snfwes_7kb&tbn8l+2#!45k&2^huhqiia(ot@zvsy2n(d'

DEBUG = True

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        'ATOMIC_REQUESTS': True,
    },
}

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# CORS
CORS_ORIGIN_ALLOW_ALL = True
