from datetime import datetime, timedelta
import json
import requests
from django.http.response import JsonResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, GenericAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin
from rest_framework.views import View, APIView
from rest_framework.viewsets import GenericViewSet
from django.shortcuts import render

from .models import *
from .serializers import *
from musicalbingo.settings import CLIENT_ID, CLIENT_SECRET


class AccessTokenViewSet(APIView):

    endpoint_url = 'https://accounts.spotify.com/api/token'

    def post(self, request):

        # Set up the data you want to send in the POST request
        data = {
            'grant_type': 'client_credentials',
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            # Add any other required data
        }

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        # Send the POST request
        response = requests.post(
            self.endpoint_url, data=data, headers=headers)

        response_data = json.loads(response.text)

        access_token = response_data['access_token']
        expires_in = response_data['expires_in']
        token_type = response_data['token_type']

        expires_at = datetime.now() + timedelta(seconds=expires_in)

        spotify_access_token = AccessToken.objects.create(
            access_token=access_token, expires_at=expires_at, token_type=token_type)

        serializer = AccessTokenSerializer(spotify_access_token)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PlaylistResponseViewSet(APIView, CreateModelMixin):
    # client_id = CLIENT_ID
    # client_secret = CLIENT_SECRET

    def get(self, request, id):
        queryset = Playlist.objects.filter(id=id).first()
        uri = queryset.playlist_uri
        fields = 'name, owner(display_name), tracks(items(track(artists(name)))), tracks(items(track(album(name)))), tracks(items(track(name))), '
        endpoint_url = f'https://api.spotify.com/v1/playlists/{uri}?fields={fields}'
        access_token = AccessToken.objects.latest('id')
        token_type = access_token.token_type
        token = access_token.access_token

        headers = {
            'Authorization': f'{token_type} {token}'
        }

        response = requests.get(endpoint_url, headers=headers)
        status = response.status_code
        response_data = json.loads(response.text)

        return Response(response_data, status=status)


class PlaylistDetail(RetrieveUpdateDestroyAPIView):
    queryset = Playlist.objects.all()
    serializer_class = PlaylistSerializer
    lookup_field = 'id'


class PlaylistDisplay(ListCreateAPIView):
    queryset = Playlist.objects.all()
    serializer_class = PlaylistSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        template = 'playlistselector/index.html'
        playlist_url = request.POST.get('playlist_url')

        if serializer.is_valid():
            start_ind = playlist_url.index('playlist/') + len('playlist/')
            end_ind = playlist_url.index('?')
            playlist_uri = playlist_url[start_ind:end_ind]
            exists = Playlist.objects.filter(
                playlist_uri=playlist_uri).exists()

            if not exists:
                Playlist.objects.create(playlist_url=playlist_url,
                                        playlist_uri=playlist_uri)
                context_data = {
                    'uri': f'https://open.spotify.com/embed/playlist/{playlist_uri}?utm_source=generator'
                }
                return render(request=request, template_name=template, context=context_data)
            else:
                context_data = {
                    'uri': f'https://open.spotify.com/embed/playlist/{playlist_uri}?utm_source=generator',
                    'status': 'It seems like that playlist has already been uploaded!'
                }
                return render(request=request, template_name=template, context=context_data)
        else:
            context_data = {
                'status': 'Try again, something seems to have been wrong...'
            }
            return render(request=request, template_name=template, context=context_data)
