from typing import Iterable, Optional
from django.db import models

# Create your models here.


class Playlist(models.Model):
    playlist_url = models.URLField(unique=True, max_length=255)
    playlist_uri = models.CharField(unique=True, max_length=255)


class AccessToken(models.Model):
    access_token = models.CharField(unique=True, max_length=255)
    token_type = models.CharField(max_length=255)
    expires_at = models.DateTimeField()
