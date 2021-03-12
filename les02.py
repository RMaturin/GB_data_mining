from pathlib import Path
from urllib.parse import urljoin
import datetime as dt
import time
import requests
import bs4
import pymongo


def get_save_path(dir_name):
    dir_path = Path(__file__).parent.joinpath(dir_name)
    if not dir_path.exists():
        dir_path.mkdir()
    return dir_path


MONTHS = {
    "янв": 1,
    "фев": 2,
    "мар": 3,
    "апр": 4,
    "май": 5,
    "мая": 5,
    "июн": 6,
    "июл": 7,
    "авг": 8,
    "сен": 9,
    "окт": 10,
    "ноя": 11,
    "дек": 12,
}


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
            if "card-sale_banner" not in prod_a.attrs.get("class"):
                product_data = self._parse(prod_a)
                self._save(product_data)

    def get_template(self):
        return {
            "url": lambda a: urljoin(self.start_url, a.attrs.get("href")),
            "promo_name": lambda a: a.find("div", attrs={"class": "card-sale__name"}).text,
            "product_name": lambda a: a.find("div", attrs={"class": "card-sale__title"}).text,
            "old_price": lambda a: float(
                ".".join(a.find("div", attrs={"class": "label__price_old"}).text.split())
            ),
            "new_price": lambda a: float(
                ".".join(a.find("div", attrs={"class": "label__price_new"}).text.split())
            ),
            "image_url": lambda a: urljoin(self.start_url, a.find("img").attrs.get("data-src")),
            "date_from": lambda a: self.__get_date(
                a.find("div", attrs={"class": "card-sale__date"}).text
            )[0],
            "date_to": lambda a: self.__get_date(
                a.find("div", attrs={"class": "card-sale__date"}).text
            )[1],
        }

    def __get_date(self, date_string) -> list:
        date_list = date_string.replace("с ", "", 1).replace("\n", "").split("до")
        result = []
        for date in date_list:
            temp_date = date.split()
            result.append(
                dt.datetime(
                    year=dt.datetime.now().year,
                    day=int(temp_date[0]),
                    month=MONTHS[temp_date[1][:3]],
                )
            )
        if result[0] > result[1]:
            result[1] = dt.datetime(result[1].year + 1, result[1].month, result[1].day,)
        return result

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
