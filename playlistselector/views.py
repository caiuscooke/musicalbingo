import json
from datetime import datetime, timedelta

import requests
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.http.response import JsonResponse
from django.shortcuts import redirect, render
from django.views import View
from rest_framework import status

from musicalbingo.settings import CLIENT_ID, CLIENT_SECRET

from .forms import *
from .models import *
from .serializers import *


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


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user=user)
            return redirect('home')
    else:
        form = AuthenticationForm()

    context = {'form': form}
    return render(request, 'playlistselector/login.html', context)


def create_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully.')
            user = authenticate(
                request, username=user.username, password=request.POST['password1'])
            if user is not None:
                login(request, user)
                return redirect('account_created')
    else:
        form = UserCreationForm()

    context_data = {
        'form': form
    }
    return render(request, 'playlistselector/createaccount.html', context=context_data)


def account_created(request):
    context = {'messages': messages.get_messages(request)}
    return render(request, 'playlistselector/accountcreated.html', context=context, status=status.HTTP_201_CREATED)


def logout_view(request):
    logout(request)
    return redirect('home')


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
        form = PlaylistForm(request.POST)

        if form.is_valid():
            playlist_url = form.cleaned_data['playlist_url']
            playlist_uri = self.get_playlist_uri(playlist_url)
            playlist = Playlist.objects.filter(
                playlist_uri=playlist_uri).first()

            if playlist:
                status = 'Another user has already uploaded that playlist.'
                self.fill_session_data(
                    request, playlist, playlist_uri, status)
                return redirect('home')
            elif len(playlist_uri) == 22:
                playlist = Playlist.objects.create(
                    playlist_url=playlist_url, playlist_uri=playlist_uri)
                status = 'Thank you for submitting your playlist!'
                self.fill_session_data(
                    request, playlist, playlist_uri, status)
                return redirect('home')
            else:
                request.session['status'] = 'That was not a valid URL'
                return redirect('home')
        else:
            request.session['status'] = 'That was not a valid URL'
            return redirect('home')


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
        playlist = Playlist.objects.filter(id=id).first()

        uri = playlist.playlist_uri
        endpoint_url = f'https://api.spotify.com/v1/playlists/{uri}'
        access_token = request.session['spotify_access_token']
        token_type = request.session['token_type']

        headers = {
            'Authorization': f'{token_type} {access_token}'
        }
        response = json.loads(requests.get(endpoint_url, headers=headers).text)

        if response.get('error'):
            context_data = {
                'error': 'That was not a valid playlist. Playlists that were made for you by Spotify (such as Spotify Wrapped) are not allowed.',
                'playlist_id': playlist.id
            }
            return render(request, template_name='playlistselector/cardgenerator.html', context=context_data)

        response_data = response.get('tracks')['items']

        next = response.get('tracks')['next']

        while next:
            response = json.loads(requests.get(
                next, headers=headers).text)

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


class PlaylistDelete(View):
    def delete(self, request, id):
        playlist = Playlist.objects.filter(id=id).first()
        playlist.delete()
        context_data = {
            'delete_status': 'That playlist was successfully deleted.',
            'playlist_info': playlist
        }
        return render(request, 'playlistselector/cardgenerator.html', context=context_data, status=status.HTTP_200_OK)


# class PlaylistDisplay(ListCreateAPIView):
    # queryset = Playlist.objects.all()
    # serializer_class = PlaylistSerializer

    # def get_playlist_uri(self, playlist_url):
    #     start_ind = playlist_url.index('playlist/') + len('playlist/')
    #     end_ind = playlist_url.index('?')
    #     playlist_uri = playlist_url[start_ind:end_ind]
    #     return playlist_uri

    # def list(self, request, *args, **kwargs):
    #     queryset = self.get_queryset()
    #     playlist_data = []
    #     for playlist in queryset:
    #         playlist_uri = playlist.playlist_uri
    #         embed_url = f'https://open.spotify.com/embed/playlist/{playlist_uri}?utm_source=generator'
    #         playlist_data.append((embed_url, playlist.id))

    #     context = {
    #         'playlist_data': playlist_data
    #     }

    #     return render(request, 'playlistselector/playlists.html', context=context)

    # def create(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     is_valid = serializer.is_valid()

    #     try:
    #         error = serializer.errors['playlist_url'][0]
    #     except:
    #         print('no error')

    #     if is_valid or 'playlist with this playlist url already exists' in error:
    #         playlist_url = request.POST.get('playlist_url')
    #         playlist_uri = self.get_playlist_uri(playlist_url)
    #         playlist = Playlist.objects.filter(
    #             playlist_uri=playlist_uri).first()

    #         if playlist:
    #             request.session['id'] = playlist.id
    #             request.session[
    #                 'embed_url'] = f'https://open.spotify.com/embed/playlist/{playlist_uri}?utm_source=generator'
    #             request.session['status'] = 'Another user has already submitted that playlist.'
    #             return redirect('home')
    #         else:
    #             playlist = Playlist.objects.create(
    #                 playlist_url=playlist_url, playlist_uri=playlist_uri)
    #             request.session['id'] = playlist.id
    #             request.session[
    #                 'embed_url'] = f'https://open.spotify.com/embed/playlist/{playlist_uri}?utm_source=generator'
    #             request.session['status'] = 'Thank you for submitting your playlist!'
    #             return redirect('home')
    #     else:
    #         request.session['status'] = f'{error}'
    #         return redirect('home')
