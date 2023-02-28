from django.shortcuts import render

from .genius import genius_search
from .utils import (
    get_album,
    get_albums,
    get_playlist,
    get_playlists,
    get_track,
    get_top_tracks,
    search_tracks,
)


# Create your views here.
def home(request):
    albums = get_albums()
    playlists = get_playlists()
    top_tracks = get_top_tracks()
    context = {"albums": albums, "playlists": playlists, "top_tracks": top_tracks}
    return render(request, "home.html", context)


def search(request):
    context = {}
    query = request.GET.get("search")
    if query is not None:
        tracks = search_tracks(query)
        context = {"tracks": tracks, "query": query}
    return render(request, "search_results.html", context)


def get_track_detail(request, track_id):
    track = get_track(track_id)
    track_name = track["name"]
    track_artist = track["primary_artist"]
    results = genius_search(f"{track_name}, {track_artist}")
    print(results)
    lyrics_path = genius_id = ""
    for i in range(len(results)):
        if results[i]["title"] == track_name or results[i]["title"] in track_name:
            lyrics_path = results[i]["url"]
            genius_id = results[i]["id"]
    context = {
        "track": track,
        "spotify_track_id": track_id,
        "lyrics_path": lyrics_path,
        "genius_id": genius_id,
    }
    return render(request, "track_detail.html", context)


def album_detail(request, album_id):
    album = get_album(album_id)
    return render(request, "album_detail.html", {"album": album})


def playlist_detail(request, playlist_id):
    playlist = get_playlist(playlist_id)
    return render(request, "playlist_detail.html", {"playlist": playlist})


def gallery(request):
    return render(request, "gallery.html")
