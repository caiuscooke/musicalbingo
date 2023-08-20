from rest_framework import serializers
from .models import *


class PlaylistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Playlist
        fields = ['playlist_url', 'playlist_uri', 'id', 'playlist_name',
                  'playlist_likes', 'playlist_genre']


class AccessTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessToken
        fields = ['access_token', 'token_type', 'expires_at']
