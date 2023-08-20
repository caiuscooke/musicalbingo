from django.urls import path
from . import views
from rest_framework.routers import SimpleRouter

# router = SimpleRouter()
# router.register('playlists', views.PlaylistViewSet)

# URL Config
urlpatterns = [
    path("gettoken/", views.AccessTokenViewSet.as_view())
    # path("getplaylist/", )
]
