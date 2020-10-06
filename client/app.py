import requests


q = "random query"
URL = f"http://127.0.0.1:8000/?q={q}"
URL2 = f"http://127.0.0.1:8000/read/"
URL3 = URL2 + "?limit=3"

r = requests.get(URL3)
print(r.status_code, r.json())