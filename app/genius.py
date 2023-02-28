import requests

from django.conf import settings

genius_access_token = settings.GENIUS_CLIENT_ACCESS_TOKEN


def genius_search(*query):
    resp = requests.get(
        f"https://api.genius.com/search?q={query}",
        headers={"authorization": f"Bearer  {genius_access_token}"},
    )
    results = []
    if resp.status_code == 200:
        resp_obj = resp.json()["response"]["hits"]
        for i in range(len(resp_obj)):
            if "Skepta" in resp_obj[i]["result"]["artist_names"]:
                results.append(resp_obj[i]["result"])
    return results
