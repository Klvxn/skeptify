import base64, requests

from django.conf import settings


access_token = settings.SPOTIFY_ACCESS_TOKEN
client_id = settings.SPOTIFY_CLIENT_ID
client_secret = settings.SPOTIFY_CLIENT_SECRET
client = f"{client_id}:{client_secret}".encode("ascii")
b64_client = base64.b64encode(client)
str_client = b64_client.decode("ascii")

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
	album_url = sk_url.format("/albums?include_groups=album")
	access_token = check_access_token()
	r = requests.get(
		album_url, headers={"Authorization": f"Bearer {access_token}"}
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
	url = sk_url.format("/top-tracks/?market=US")
	access_token = check_access_token()
	resp = requests.get(url, headers={"Authorization": f"Bearer {access_token}"}).json()
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
	sp_url = f"https://api.spotify.com/v1/tracks/{track_id}"
	access_token = check_access_token()
	resp = requests.get(
		sp_url, headers={"Authorization": f"Bearer {access_token}"}
	).json()
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
		"7xduk93ZbtAg2y4QyIJrGc"
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
	query_url = f"https://api.spotify.com/v1/search?q={query}+Skepta&type=track&limit=5"
	access_token = check_access_token()
	resp = requests.get(
		query_url, headers={"Authorization": f"Bearer {access_token}"}
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
