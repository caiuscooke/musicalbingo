import json
import logging
from datetime import datetime, timedelta

import requests
from django.http.response import JsonResponse
from django.shortcuts import redirect, render
from django.views import View
from rest_framework import status

from musicalbingo.settings.common import CLIENT_ID, CLIENT_SECRET

from .forms import *
from .models import *
from .pdfgenerator import make_bingo_card
from .serializers import *

logger = logging.getLogger(__name__)


def home(request):
    status = request.session.pop('status', None)
    embed_url = request.session.pop('embed_url', None)
    id = request.session.pop('id', None)
    track_names = request.session.pop('track_names', None)
    context = {
        'status': status,
        'embed_url': embed_url,
        'track_names': track_names,
        'id': id,
    }
    return render(request, 'playlistselector/home.html', context)


class PlaylistCreate(View):

    def get_playlist_uri(self, playlist_url):
        start_ind = playlist_url.index('playlist/') + len('playlist/')
        end_ind = playlist_url.index('?')
        playlist_uri = playlist_url[start_ind:end_ind]
        return playlist_uri

    def get(self, request, *args, **kwargs):
        queryset = Playlist.objects.all()
        playlist_data = []
        for playlist in queryset:
            playlist_uri = playlist.playlist_uri
            embed_url = f'https://open.spotify.com/embed/playlist/{playlist_uri}?utm_source=generator'
            playlist_data.append((embed_url, playlist.id))

        template_name = 'playlistselector/playlists.html'
        context = {
            'playlist_data': playlist_data
        }

        return render(request, template_name, context=context)

    def fill_session_data(self, request: requests.request, playlist: Playlist, playlist_uri: str, status: str):
        request.session['id'] = playlist.id
        request.session[
            'embed_url'] = f'https://open.spotify.com/embed/playlist/{playlist_uri}?utm_source=generator'
        request.session['status'] = status

    def post(self, request, *args, **kwargs):
        uri_required_length = 22
        form = PlaylistForm(request.POST)

        if not form.is_valid():
            request.session['status'] = 'That was not a valid URL'
            return redirect('musical-bingo')

        playlist_url = form.cleaned_data['playlist_url']
        response = requests.get(playlist_url)
        playlist_url = response.url

        try:
            playlist_uri = self.get_playlist_uri(playlist_url)
        except:
            request.session['status'] = 'That was not a valid URL'
            return redirect('musical-bingo')

        playlist = Playlist.objects.filter(
            playlist_uri=playlist_uri).first()

        if playlist:
            status = 'Another user has already uploaded that playlist.'
            self.fill_session_data(
                request, playlist, playlist_uri, status)
            return redirect('musical-bingo')
        elif len(playlist_uri) == uri_required_length:
            playlist = Playlist.objects.create(
                playlist_url=playlist_url, playlist_uri=playlist_uri)
            status = 'Thank you for submitting your playlist!'
            self.fill_session_data(
                request, playlist, playlist_uri, status)
            return redirect('musical-bingo')


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

    def post(self, request, id):
        print(
            f"the csrf middleware token is: {request.POST.get('csrfmiddlewaretoken')}")
        # Set up for all playlists
        playlist = Playlist.objects.filter(id=id).first()
        cards = int(request.POST.get('cards'))
        uri = playlist.playlist_uri
        offset = 0
        endpoint_url = f'https://api.spotify.com/v1/playlists/{uri}/tracks?offset={offset}&limit=100'
        access_token = request.session['spotify_access_token']
        token_type = request.session['token_type']

        headers = {
            'Authorization': f'{token_type} {access_token}'
        }
        response = requests.get(endpoint_url, headers=headers)
        data = response.json()
        total = data.get('total')

        if total < 25:
            request.session['status'] = 'That playlist is too small. It needs to have at least 25 songs to work with musical bingo!'
            playlist.delete()
            return redirect('musical-bingo')

        items = data.get('items')
        track_names = [item.get('track')['name'] for item in items]

        offset_interval = 100

        # skip everything if there is only one query to get
        if total < 100:
            return make_bingo_card(track_names=track_names, unique_pages=cards)
        elif total > 1000:
            offset_interval = 200

        while total - offset > 100:
            offset += offset_interval
            endpoint_url = f'https://api.spotify.com/v1/playlists/{uri}/tracks?offset={offset}&limit=100'
            response = requests.get(endpoint_url, headers=headers)
            data = response.json()
            items = data.get('items')
            track_names.extend(item.get('track')['name'] for item in items)

        return make_bingo_card(track_names=track_names, unique_pages=cards)


class PlaylistDelete(View):
    def delete(self, request, id):
        playlist = Playlist.objects.filter(id=id).first()
        playlist.delete()
        context_data = {
            'delete_status': 'That playlist was successfully deleted.',
            'playlist_info': playlist
        }
        return render(request, 'playlistselector/cardgenerator.html', context=context_data, status=status.HTTP_200_OK)
