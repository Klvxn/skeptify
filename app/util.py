import requests, spotipy

from django.conf import settings
from spotipy.oauth2 import SpotifyClientCredentials


client_id = settings.SPOTIFY_CLIENT_ID
client_secret = settings.SPOTIFY_CLIENT_SECRET
genius_access_token = settings.GENIUS_ACCESS_TOKEN

client_cred = SpotifyClientCredentials(
    client_id=client_id,
    client_secret=client_secret,
)
sp = spotipy.Spotify(client_credentials_manager=client_cred)


def albums():
    albums_response = sp.artist_albums("2p1fiYHYiXz9qi0JJyxBzN", album_type="album")
    albums = []
    for item in albums_response["items"]:
        album_info = {
            "id": item["id"],
            "name": item["name"],
            "release_date": item["release_date"][:4],
            "image_url": item["images"][1]["url"],
        }
        albums.append(album_info)
    return albums


def single_album(album_id):
    album_response = sp.album(album_id)
    album_info = {
        "id": album_response["id"],
        "name": album_response["name"],
        "release_date": album_response["release_date"][:4],
        "total_tracks": album_response["total_tracks"],
        "image_url": album_response["images"][1]["url"],
        "label": album_response["label"],
        "artists": [artist["name"] for artist in album_response["artists"]],
        "copyright": album_response["copyrights"][0]["text"],
        "ext_url": album_response["external_urls"]["spotify"],
    }
    album_tracks = []
    for item in album_response["tracks"]["items"]:
        track = {
            "name": item["name"],
            "track_number": item["track_number"],
        }
        album_tracks.append(track)
    album_info["tracks"] = album_tracks
    return album_info


def top_tracks():
    tracks_response = sp.artist_top_tracks("2p1fiYHYiXz9qi0JJyxBzN")
    tracks = []
    for item in tracks_response["tracks"]:
        tracks_info = {
            "id": item["id"],
            "name": item["name"],
            "preview_url": item["preview_url"],
            "image_url": item["album"]["images"][1]["url"],
            "primary_artist": item["artists"][0]["name"],
        }
        tracks.append(tracks_info)
    return tracks


def single_track(track_id):
    track_response = sp.track(track_id)
    track_info = {
        "name": track_response["name"],
        "ext_url": track_response["external_urls"]["spotify"],
        "type": track_response["album"]["album_type"],
        "primary_artist": track_response["artists"][0]["name"],
        "release_date": track_response["album"]["release_date"],
        "album_name": track_response["album"]["name"],
        "image_url": track_response["album"]["images"][1]["url"],
    }
    return track_info


def playlists(
    playlist_id=[
        "37i9dQZF1E4Ap9589A8DyD",
        "37i9dQZF1DX5WbJFtYTzv7",
        "0dah37LJDy5rqZ5pxZ8sYN",
        "556xSCGlcyud3bVfTvNrwM",
        "7xduk93ZbtAg2y4QyIJrGc",
    ]
):
    if isinstance(playlist_id, list):
        playlists = []
        for id in playlist_id:
            playlist_response = sp.playlist(
                playlist_id=id,
                fields="id,name,owner(display_name),description,images.url",
                additional_types=["track"],
            )
            playlist_info = {key: value for key, value in playlist_response.items()}
            playlist_info["image_url"] = playlist_response["images"][0]["url"]
            playlists.append(playlist_info)
        return playlists
    fields = "id,name,owner(display_name),description,followers(total),images(url),external_urls(spotify),tracks(total)"
    playlist_response = sp.playlist(
        playlist_id,
        fields=fields,
        additional_types=["track"],
    )
    playlist = {key: value for key, value in playlist_response.items()}
    playlist["image_url"] = playlist_response["images"][0]["url"]
    playlist["playlist_tracks"] = sp.playlist_tracks(
        playlist_id, fields="items.track(name)"
    )
    return playlist


def search_tracks(query):
    response = sp.search(f"{query}+Skepta", limit=4, type="album,track")
    songs = []
    for item in response["items"]:
        song_info = {
            "title": item["name"],
            "artists": [artist["name"] for artist in item["artists"]],
            "image_url": item["album"]["images"][1]["url"],
            "spotify_id": item["id"],
        }
        songs.append(song_info)
    return songs


def genius_search(*query):
    resp = requests.get(
        f"https://api.genius.com/search?q={query}",
        headers={"authorization": f"Bearer {genius_access_token}"},
    )
    results = []
    if resp.status_code == 200:
        resp_obj = resp.json()["response"]["hits"]
        for i in range(len(resp_obj)):
            if "Skepta" in resp_obj[i]["result"]["artist_names"]:
                results.append(resp_obj[i]["result"])
    return results
