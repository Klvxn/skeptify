import base64, requests
import spotipy

from django.conf import settings
from spotipy.oauth2 import SpotifyOAuth


access_token = settings.SPOTIFY_ACCESS_TOKEN
client_id = settings.SPOTIFY_CLIENT_ID
client_secret = settings.SPOTIFY_CLIENT_SECRET
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
    album_url = sk_url.format("/albums")
    access_token = check_access_token()
    r = requests.get(
        album_url,
        headers={"Authorization": f"Bearer {access_token}"},
        params={"include_groups": "album"},
    ).json()
    albums = []
    for a in r["items"]:
        album = {
            "id": a["id"],
            "name": a["name"],
            "release_date": a["release_date"][:4],
            "image_url": a["images"][1]["url"],
        }
        albums.append(album)
    return albums


def get_album(album_id):
    album_url = base_url.format(f"/albums/{album_id}")
    access_token = check_access_token()
    resp = requests.get(
        album_url, headers={"Authorization": f"Bearer {access_token}"}
    ).json()
    album = {
        "id": resp["id"],
        "name": resp["name"],
        "genres": resp["genres"],
        "release_date": resp["release_date"][:4],
        "total_tracks": resp["total_tracks"],
        "image_url": resp["images"][1]["url"],
        "label": resp["label"],
        "artists": [artist["name"] for artist in resp["artists"]],
        "copyright": resp["copyrights"][0]["text"],
        "ext_url": resp["external_urls"]["spotify"],
    }
    album_tracks = []
    for item in resp["tracks"]["items"]:
        track = {
            "name": item["name"],
            "id": item["id"],
            "track_number": item["track_number"],
            "artists": [artist["name"] for artist in item["artists"]],
        }
        album_tracks.append(track)
    album["tracks"] = album_tracks
    return album


def get_top_tracks():
    url = sk_url.format("/top-tracks")
    access_token = check_access_token()
    resp = requests.get(
        url,
        headers={"Authorization": f"Bearer {access_token}"},
        params={"market": "US"},
    ).json()
    tracks = []
    for t in resp["tracks"]:
        track = {
            "id": t["id"],
            "name": t["name"],
            "preview_url": t["preview_url"],
            "image_url": t["album"]["images"][1]["url"],
            "primary_artist": t["artists"][0]["name"],
        }
        tracks.append(track)
    return tracks


def get_track(track_id):
    url = base_url.format(f"/tracks/{track_id}")
    access_token = check_access_token()
    resp = requests.get(url, headers={"Authorization": f"Bearer {access_token}"}).json()
    track_details = {
        "name": resp["name"],
        "ext_url": resp["external_urls"]["spotify"],
        "type": resp["album"]["album_type"],
        "primary_artist": resp["artists"][0]["name"],
        "release_date": resp["album"]["release_date"],
        "album_name": resp["album"]["name"],
        "image_url": resp["album"]["images"][1]["url"],
    }
    return track_details


def get_playlists():
    playlist_ids = [
        "37i9dQZF1E4Ap9589A8DyD",
        "37i9dQZF1DX5WbJFtYTzv7",
        "0dah37LJDy5rqZ5pxZ8sYN",
        "556xSCGlcyud3bVfTvNrwM",
        "7xduk93ZbtAg2y4QyIJrGc",
    ]
    playlists = []
    for id in playlist_ids:
        playlist_url = base_url.format(f"/playlists/{id}")
        access_token = check_access_token()
        resp = requests.get(
            playlist_url, headers={"Authorization": f"Bearer {access_token}"}
        ).json()
        pl = {
            "id": resp["id"],
            "name": resp["name"],
            "owner": resp["owner"]["display_name"],
            "desc": resp["description"],
            "followers": resp["followers"]["total"],
            "image_url": resp["images"][0]["url"],
            "total_tracks": resp["tracks"]["total"],
            "ext_url": resp["external_urls"]["spotify"],
        }
        playlists.append(pl)
    return playlists


def get_playlist(playlist_id):
    playlist_url = base_url.format(f"/playlists/{playlist_id}")
    access_token = check_access_token()
    resp = requests.get(
        playlist_url, headers={"Authorization": f"Bearer {access_token}"}
    ).json()
    playlist = {
        "id": resp["id"],
        "name": resp["name"],
        "owner": resp["owner"]["display_name"],
        "desc": resp["description"],
        "image_url": resp["images"][0]["url"],
        "total_tracks": resp["tracks"]["total"],
        "ext_url": resp["external_urls"]["spotify"],
    }
    playlist_tracks = []
    total_tracks = resp["tracks"]["total"]
    for item in resp["tracks"]["items"]:
        track = {
            "name": item["track"]["name"],
            "id": item["track"]["id"],
            "total_tracks": total_tracks,
            "artists": [artist["name"] for artist in item["track"]["artists"]],
        }
        playlist_tracks.append(track)
    playlist["tracks"] = playlist_tracks
    return playlist


def search_tracks(query):
    songs = []
    query_url = f"https://api.spotify.com/v1/search"
    access_token = check_access_token()
    resp = requests.get(
        query_url,
        headers={"Authorization": f"Bearer {access_token}"},
        params={"q": f"{query}%20artist:Skepta", "type": "album, track", "limit": 5},
    ).json()
    for item in resp["tracks"]["items"]:
        song_details = {
            "title": item["name"],
            "artists": [artist["name"] for artist in item["artists"]],
            "image_url": item["album"]["images"][1]["url"],
            "spotify_id": item["id"],
        }
        songs.append(song_details)
    return songs[:4]


def get_user():
    user_info = sp.current_user()
    user = {
        "name": user_info["display_name"],
        "image_url": user_info["images"][0]["url"],
    }
    return user


def get_user_top_artists():
    items = []
    sp_range = ["short_term", "medium_term", "long_term"]
    for range in sp_range:
        top_artists = sp.current_user_top_artists(limit=10, time_range=range)
        artists = []
        for idx, i in enumerate(top_artists["items"], start=1):
            artist_info = {
                "idx": idx,
                "name": i["name"],
                "image_url": i["images"][0]["url"],
                "ext_url": i["external_urls"]["spotify"],
            }
            artists.append(artist_info)
        artists_by_range = {f"{range}_artists": artists}
        items.append(artists_by_range)
    return items


def get_user_top_tracks():
    items = []
    sp_range = ["short_term", "medium_term", "long_term"]
    for range in sp_range:
        tracks = []
        top_tracks = sp.current_user_top_tracks(limit=10, time_range=range)
        for idx, i in enumerate(top_tracks["items"], start=1):
            track_info = {
                "idx": idx,
                "name": i["name"],
                "image_url": i["album"]["images"][1]["url"],
                "ext_url": i["external_urls"]["spotify"],
                "primary_artist": i["artists"][0]["name"],
            }
            tracks.append(track_info)
        tracks_by_range = {f"{range}_tracks": tracks}
        items.append(tracks_by_range)
    return items
