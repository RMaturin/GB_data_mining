from pathlib import Path
from urllib.parse import urljoin
import time
import requests
import bs4
import pymongo


def get_save_path(dir_name):
    dir_path = Path(__file__).parent.joinpath(dir_name)
    if not dir_path.exists():
        dir_path.mkdir()
    return dir_path


class MagnitParse:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36"
    }

    def __init__(self, start_url, db_client):
        self.start_url = start_url
        self.db = db_client["gd_data_mining"]
        self.collection = self.db["magnit_products"]

    def _get_response(self, url):
        while True:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response
            time.sleep(0.5)

    def _get_soup(self, url):
        # TODO: обработка ошибок
        response = self._get_response(url)
        return bs4.BeautifulSoup(response.text, "lxml")

    def run(self):
        soup = self._get_soup(self.start_url)
        catalog = soup.find("div", attrs={"class": "сatalogue__main"})
        for prod_a in catalog.find_all("a", recursive=False):
            product_data = self._parse(prod_a)
            self._save(product_data)

    def get_template(self):
        return {
            "url": lambda a: urljoin(self.start_url, a.attrs.get("href")),
            "promo_name": lambda a: a.find("div", attrs={"class": "card-sale__name"}).text,
            "product_name": lambda a: a.find("div", attrs={"class": "card-sale__title"}).text
            # "old_price": lambda a: float(
            #     ".".join(
            #         itm for itm in a.find("div", attrs={"class": "label__price_old"}).text.split()
            #     )
            # ),
            # "new_price": lambda a: float(
            #     ".".join(
            #         itm for itm in a.find("div", attrs={"class": "label__price_new"}).text.split()
            #     )
            # ),
            # "image_url": lambda a: urljoin(self.start_url, a.find("img").attrs.get("data-src")),
            # "date_from": lambda a: self.__get_date(
            #     a.find("div", attrs={"class": "card-sale__date"}).text
            # )[0],
            # "date_to": lambda a: self.__get_date(
            #     a.find("div", attrs={"class": "card-sale__date"}).text
            # )[1],
        }

    def _parse(self, product_a):
        data = {}
        for key, funk in self.get_template().items():
            try:
                data[key] = funk(product_a)
            except (AttributeError, ValueError):
                pass
        return data

    # def _save(self, data: dict, file_path: Path):
    #     file_path.write_text(json.dumps(data, ensure_ascii=False), encoding="UTF-8")
    def _save(self, data: dict):
        self.collection.insert_one(data)


if __name__ == "__main__":
    url = "https://magnit.ru/promo/"
    db_client = pymongo.MongoClient("mongodb://localhost:27017")
    parser = MagnitParse(url, db_client)
    parser.run()
