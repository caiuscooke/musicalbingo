from rest_framework import serializers
from .models import *


class PlaylistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Playlist
        fields = ['id', 'playlist_url', 'playlist_uri']

    playlist_uri = serializers.CharField(read_only=True)


class AccessTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessToken
        fields = ['access_token', 'token_type', 'expires_at']
