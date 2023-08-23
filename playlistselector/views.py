import json
from datetime import datetime, timedelta

import requests
from django.http.response import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from rest_framework import status
from rest_framework.generics import (GenericAPIView, ListCreateAPIView,
                                     RetrieveUpdateDestroyAPIView)
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin
from rest_framework.response import Response
from rest_framework.views import APIView, View
from rest_framework.viewsets import GenericViewSet

from musicalbingo.settings import CLIENT_ID, CLIENT_SECRET

from .models import *
from .serializers import *


def home(request):
    status = request.session.pop('status', None)
    uri = request.session.pop('uri', None)
    id = request.session.pop('id', None)
    track_names = request.session.pop('track_names', None)
    context = {
        'status': status,
        'uri': uri,
        'track_names': track_names,
        'id': id
    }
    return render(request, 'playlistselector/index.html', context)


class AccessTokenViewSet(View):

    endpoint_url = 'https://accounts.spotify.com/api/token'
    # initializes these variables so it can be used in if statements
    data = {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        # Add any other required data
    }

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    def spotify_send_post(self, request):
        response = requests.post(
            self.endpoint_url, data=self.data, headers=self.headers)

        response_data = json.loads(response.text)

        access_token = response_data['access_token']
        request.session['spotify_access_token'] = access_token

        token_type = response_data['token_type']
        request.session['token_type'] = token_type

        expires_in = response_data['expires_in']
        expires_at = datetime.now() + timedelta(seconds=expires_in)
        expires_at_str = datetime.strftime(expires_at,
                                           '%Y-%m-%d %H:%M:%S')
        request.session['a_t_expires_at'] = expires_at_str
        return {'spotify_access_token': access_token, 'a_t_expires_at': expires_at_str, 'token_type': token_type}

    def get_access_token(self, request):
        access_token = request.session.get('spotify_access_token')
        token_type = request.session.get('token_type')
        expires_at_str = request.session.get('a_t_expires_at')

        if access_token is None or expires_at_str is None:
            return self.spotify_send_post(request)
        else:
            expires_at = datetime.strptime(expires_at_str, '%Y-%m-%d %H:%M:%S')
            if expires_at <= datetime.now():
                return self.spotify_send_post(request)
            else:
                return {'spotify_access_token': access_token, 'a_t_expires_at': expires_at_str, 'token_type': token_type}

    def get(self, request, *args, **kwargs):
        access_token = self.get_access_token(request)
        return JsonResponse({'access_token': access_token})


class PlaylistResponseViewSet(View):

    def get(self, request, id):
        queryset = Playlist.objects.filter(id=id).first()
        uri = queryset.playlist_uri

        endpoint_url = f'https://api.spotify.com/v1/playlists/{uri}'
        access_token = request.session['spotify_access_token']
        token_type = request.session['token_type']

        headers = {
            'Authorization': f'{token_type} {access_token}'
        }
        response = json.loads(requests.get(endpoint_url, headers=headers).text)
        response_data = response.get('tracks')['items']
        next = response.get('tracks')['next']
        entry = 1
        while next:
            response = json.loads(requests.get(
                next, headers=headers).text)
            entry += 1
            response_data.append(response['items'])
            if response.get('next'):
                next = response.get('next')
            else:
                break

        track_names = []

        for each in response_data:
            if type(each) == dict:
                try:
                    track_name = each.get('track')['name']
                    track_names.append(track_name)
                except:
                    pass
            elif type(each) == list:
                for item in each:
                    try:
                        track_name = item.get('track')['name']
                        track_names.append(track_name)
                    except:
                        pass
        track_total = len(track_names)
        track_names.sort()
        track_names.insert(0, track_total)

        context_data = {
            'track_names': track_names
        }
        return render(request, template_name='playlistselector/cardgenerator.html', context=context_data)


class PlaylistDetail(RetrieveUpdateDestroyAPIView):
    queryset = Playlist.objects.all()
    serializer_class = PlaylistSerializer
    lookup_field = 'id'


class PlaylistDisplay(ListCreateAPIView):
    queryset = Playlist.objects.all()
    serializer_class = PlaylistSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        playlist_data = []
        for playlist in queryset:
            playlist_url = playlist.playlist_url
            start_ind = playlist_url.index('playlist/') + len('playlist/')
            end_ind = playlist_url.index('?')
            playlist_uri = playlist_url[start_ind:end_ind]
            embed_url = f'https://open.spotify.com/embed/playlist/{playlist_uri}?utm_source=generator'
            playlist_data.append((embed_url, playlist.id))

        context = {
            'playlist_data': playlist_data
        }

        return render(request, 'playlistselector/playlists.html', context=context)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        playlist_url = request.POST.get('playlist_url')

        if serializer.is_valid():
            start_ind = playlist_url.index('playlist/') + len('playlist/')
            end_ind = playlist_url.index('?')
            playlist_uri = playlist_url[start_ind:end_ind]
            exists = Playlist.objects.filter(
                playlist_uri=playlist_uri).exists()

            if not exists:
                playlist = Playlist.objects.create(playlist_url=playlist_url,
                                                   playlist_uri=playlist_uri)
                playlist_id = playlist.id
                request.session['id'] = playlist_id
                request.session[
                    'playlist_embed'] = f'https://open.spotify.com/embed/playlist/{playlist_uri}?utm_source=generator'
                return redirect('home')
            else:
                playlist = Playlist.objects.get(playlist_uri=playlist_uri)
                playlist_id = playlist.id
                request.session['id'] = playlist_id
                request.session[
                    'uri'] = f'https://open.spotify.com/embed/playlist/{playlist_uri}?utm_source=generator'
                request.session['status'] = 'It seems like that playlist has already been uploaded by a user!'
                return redirect('home')
        else:
            request.session['status'] = f"That wasn't a valid URL, please try again."
            return redirect('home')
