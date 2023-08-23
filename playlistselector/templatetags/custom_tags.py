from datetime import datetime, timedelta
from django import template

register = template.Library()


@register.filter(name='has_expired')
def has_expired(expiry_datetime):
    expiry_datetime = datetime.strptime(expiry_datetime, '%Y-%m-%d %H:%M:%S')
    return expiry_datetime <= datetime.now()
