import base64, os
import requests, spotipy

from dotenv import load_dotenv
from django.conf import settings
from spotipy.oauth2 import SpotifyOAuth


load_dotenv()

access_token = os.environ.get("SPOTIFY_ACCESS_TOKEN")
client_id = os.environ.get("SPOTIFY_CLIENT_ID")
client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")
client = f"{client_id}:{client_secret}".encode("ascii")
b64_client = base64.b64encode(client)
str_client = b64_client.decode("ascii")

auth_manager = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri="http://localhost:8000/callback/",
    scope="user-top-read",
    show_dialog=True,
)
sp = spotipy.Spotify(auth_manager=auth_manager)

base_url = "https://api.spotify.com/v1{}"
sk_url = "https://api.spotify.com/v1/artists/2p1fiYHYiXz9qi0JJyxBzN{}"


def refresh_access_token() -> str | None:
    r = requests.post(
        "https://accounts.spotify.com/api/token",
        headers={"Authorization": f"Basic {str_client}"},
        data={"grant_type": "client_credentials"},
    )
    if r.status_code == 200:
        settings.SPOTIFY_ACCESS_TOKEN = access_token = r.json()["access_token"]
        return access_token
    print(r.json())


def check_access_token():
    try:
        resp = requests.get(
            sk_url, headers={"Authorization": f"Bearer {access_token}"}
        ).json()
        print(resp["artists"])
        return access_token
    except KeyError:
        new_token = refresh_access_token()
        return new_token


def get_albums():
    albums_response = sp.artist_albums("2p1fiYHYiXz9qi0JJyxBzN", album_type="album")
    albums = []
    for item in albums_response["items"]:
        album_info = {
            "id": item["id"],
            "name": item["name"],
            "release_date": item["release_date"][:4],
            "image_url": item["images"][1]["url"],
        }
        album.append(album_info)
    return albums


def get_album(album_id):
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


def get_top_tracks():
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


def get_track(track_id):
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


def get_playlists(
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
    # results = sp.search(f"{query}+Skepta", limit=4, type="track,album")
    songs = []
    query_url = f"https://api.spotify.com/v1/search"
    access_token = check_access_token()
    resp = requests.get(
        query_url,
        headers={"Authorization": f"Bearer {access_token}"},
        params={"q": f"{query}%20artist:Skepta", "type": "track", "limit": 4},
    ).json()
    for item in resp["tracks"]["items"]:
        song_info = {
            "title": item["name"],
            "artists": [artist["name"] for artist in item["artists"]],
            "image_url": item["album"]["images"][1]["url"],
            "spotify_id": item["id"],
        }
        songs.append(song_info)
    return songs


def get_user():
    user_response = sp.current_user()
    user_info = {
        "name": user_response["display_name"],
        "image_url": user_response["images"][0]["url"],
    }
    return user_info


def get_user_top_artists():
    top_artists = []
    sp_range = ["short_term", "medium_term", "long_term"]
    for range in sp_range:
        top_artists_response = sp.current_user_top_artists(limit=10, time_range=range)
        artists = []
        for idx, item in enumerate(top_artists_response["items"], start=1):
            artist_info = {
                "idx": idx,
                "name": item["name"],
                "image_url": item["images"][0]["url"],
                "ext_url": item["external_urls"]["spotify"],
            }
            artists.append(artist_info)
        artists_by_range = {f"{range}_artists": artists}
        top_artists.append(artists_by_range)
    return top_artists


def get_user_top_tracks():
    top_tracks = []
    sp_range = ["short_term", "medium_term", "long_term"]
    for range in sp_range:
        tracks = []
        top_tracks_response = sp.current_user_top_tracks(limit=10, time_range=range)
        for idx, item in enumerate(top_tracks_response["items"], start=1):
            track_info = {
                "idx": idx,
                "name": item["name"],
                "image_url": item["album"]["images"][1]["url"],
                "ext_url": item["external_urls"]["spotify"],
                "primary_artist": item["artists"][0]["name"],
            }
            tracks.append(track_info)
        tracks_by_range = {f"{range}_tracks": tracks}
        top_tracks.append(tracks_by_range)
    return top_tracks
