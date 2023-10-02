from .common import *
import dj_database_url

DEBUG = False
ALLOWED_HOSTS = ['caiuscooke-portfolio-prod-299a3e37b550.herokuapp.com/']

DATABASES = {
    'default': dj_database_url.config()
}

EMAIL_HOST = os.environ['MAILGUN_SMTP_SERVER']
EMAIL_HOST_USER = os.environ['MAILGUN_SMTP_LOGIN']
EMAIL_HOST_PASSWORD = os.environ['MAILGUN_SMTP_PASSWORD']
EMAIL_PORT = os.environ['MAILGUN_SMTP_PORT']
