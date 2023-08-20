from datetime import datetime, timedelta
import json
import requests
from django.http.response import JsonResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.views import View, APIView
from rest_framework.viewsets import GenericViewSet

from .models import *
from .serializers import *


# class PlaylistViewSet(CreateModelMixin, ListModelMixin, GenericViewSet):
#     queryset = Playlist.objects.all()
#     serializer_class = PlaylistSerializer

#     def create(self, request, *args, **kwargs):
#         serializer_data = self.get_serializer(request.data)
#         serializer = serializer_data
#         playlist_url = request.data['playlist_url']
#         uri_start = playlist_url.index('playlist/') + 9
#         uri_end = playlist_url.index('?')
#         uri = playlist_url[uri_start:uri_end]
#         serializer['playlist_uri'] = uri
#         serializer.is_valid(raise_exception=True)
#         self.perform_create(serializer)
#         return HttpResponse(serializer.data, status=status.HTTP_201_CREATED)

# class PlayListViewSet(APIView):
#     def get(self, request):


class AccessTokenViewSet(APIView):
    # Set up your Spotify API credentials
    client_id = '53ee2e6b07c247b5bee73008cb912c35'
    client_secret = '0dedf33cc1c6455aa836c85f31f3ee2a'
    # Set up the endpoint URL
    endpoint_url = 'https://accounts.spotify.com/api/token'

    def post(self, request):

        # Set up the data you want to send in the POST request
        data = {
            'grant_type': 'client_credentials',
            'client_id': AccessTokenViewSet.client_id,
            'client_secret': AccessTokenViewSet.client_secret,
            # Add any other required data
        }

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        # Send the POST request
        response = requests.post(
            AccessTokenViewSet.endpoint_url, data=data, headers=headers)

        response_data = json.loads(response.text)

        access_token = response_data['access_token']
        expires_in = response_data['expires_in']
        token_type = response_data['token_type']

        expires_at = datetime.now() + timedelta(seconds=expires_in)

        spotify_access_token = AccessToken.objects.create(
            access_token=access_token, expires_at=expires_at, token_type=token_type)

        serializer = AccessTokenSerializer(spotify_access_token)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# # Handle the response as needed
# if response.status_code == 200:
#     return Response(serializer.data)
# else:
#     status = response.status_code
#     return JsonResponse({'message': f'POST request failed, status = {status}'}, status=status)
