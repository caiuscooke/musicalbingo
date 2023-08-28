from django.urls import include, path
from django.views.generic import TemplateView
from . import views
from rest_framework.routers import DefaultRouter

# router = SimpleRouter()
# router.register('playlists', views.PlaylistViewSet)

# URL Config
urlpatterns = [
    path("", views.home, name='home'),
    path("get-access-token/", views.AccessTokenViewSet.as_view(),
         name='get_access_token'),
    path("playlist/", views.PlaylistCreate.as_view(), name='playlist'),
    path("playlist/<int:id>/get-bingo-cards/",
         views.PlaylistResponseViewSet.as_view(), name='get_info'),
    path("playlist/<int:id>/", views.PlaylistDelete.as_view()),
    path("accounts/create", views.create_user, name='create'),
    path("accounts/created", views.account_created, name='account_created'),
    path("accounts/logout", views.logout_view, name='logout'),
    path("accounts/login", views.login_view, name='login'),
]
