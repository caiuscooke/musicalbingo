from django.db import models

# Create your models here.


class Playlist(models.Model):
    playlist_url = models.URLField(unique=True, max_length=255)
    playlist_uri = models.CharField(unique=True, max_length=255)
    playlist_name = models.CharField(max_length=255)
    playlist_likes = models.PositiveBigIntegerField()
    playlist_genre = models.CharField(max_length=255)
    published_by = models.CharField(max_length=255)
    date_added = models.DateTimeField(auto_now_add=True)


class AccessToken(models.Model):
    access_token = models.CharField(unique=True, max_length=255)
    token_type = models.CharField(max_length=255)
    expires_at = models.DateTimeField()

# class Card:
#     card_id = models.PositiveIntegerField()
#     playlist_url = models.ForeignKey(Playlist, on_delete=models.CASCADE)


# class Song:
#     song_id = models.PositiveIntegerField(primary_key=True, unique=True)
#     title = models.CharField(max_length=255)
#     author = models.CharField(max_length=255)
#     genre = models.CharField(max_length=255)
#     date_created = models.DateField()
