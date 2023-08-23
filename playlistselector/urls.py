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
    path("playlist/", views.PlaylistDisplay.as_view(), name='playlist'),
    path("playlist/<int:id>/get-full-info/",
         views.PlaylistResponseViewSet.as_view(), name='get_info'),
    path("playlist/<int:id>/", views.PlaylistDetail.as_view()),
]
