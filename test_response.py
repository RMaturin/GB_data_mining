import requests
from pathlib import Path


url = "https://magnit.ru/promo/"
file_path = Path(__file__).parent.joinpath("magnit.html")
response = requests.get(url)
file_path.write_bytes(response.content)
