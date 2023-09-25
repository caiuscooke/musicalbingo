from .common import *

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'musicalbingodb',
        'HOST': 'localhost',
        'USER': 'root',
        'PASSWORD': 'L0st%+L0st'
    }
}

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'cookecaius@gmail.com'
EMAIL_HOST_PASSWORD = 'svcz etaj jano krht'
