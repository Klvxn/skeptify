from django.urls import path

from .views import (
    album_detail,
    stats_home,
    track_detail,
    home,
    playlist_detail,
    search,
    user_stats,
)


app_name = "app"
urlpatterns = [
    path("", home),
    path("tracks/<str:track_id>/", track_detail, name="track_detail"),
    path("albums/<str:album_id>/", album_detail, name="album_detail"),
    path("playlists/<str:playlist_id>/", playlist_detail, name="playlist_detail"),
    path("find-track/", search, name="search"),
    path("spotify-stats/home/", stats_home, name="stats_home"),
    path("me/spotify-stats/", user_stats, name="stats"),
]
