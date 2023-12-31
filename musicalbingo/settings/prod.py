from .common import *
import dj_database_url

DEBUG = False

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True

ALLOWED_HOSTS = [
    'caiuscooke-portfolio-prod-299a3e37b550.herokuapp.com', 'caiuscooke.com']

DATABASES = {
    'default': dj_database_url.config()
}

EMAIL_HOST = os.environ.get('MAILGUN_SMTP_SERVER', '')
EMAIL_PORT = os.environ.get('MAILGUN_SMTP_PORT', '')
EMAIL_HOST_USER = os.environ.get('MAILGUN_SMTP_LOGIN', '')
EMAIL_HOST_PASSWORD = os.environ.get('MAILGUN_SMTP_PASSWORD', '')
