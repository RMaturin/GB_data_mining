"""
Источник: https://5ka.ru/special_offers/

Задача организовать сбор данных,
необходимо иметь метод сохранения данных в .json файлы

результат: Данные скачиваются с источника, при вызове метода/функции сохранения в файл скачанные данные сохраняются в
Json файлы, для каждой категории товаров должен быть создан отдельный файл и содержать товары исключительно
соответсвующие данной категории.

пример структуры данных для файла:

{
"name": "имя категории",
"code": "Код соответсвующий категории (используется в запросах)",
"products": [{PRODUCT},  {PRODUCT}........] # список словарей товаров соответсвующих данной категории
}
"""

import requests
import time
import json
from pathlib import Path


class Parse5ka:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36"
    }

    def __init__(self, start_url: str, save_path: Path):
        self.start_url = start_url
        self.save_path = save_path

    def _get_response(self, url):
        while True:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response
            time.sleep(0.5)

    def run(self):
        for product in self._parse(self.start_url):
            product_path = self.save_path.joinpath(f'{product["id"]}.json')
            self._save(product, product_path)

    def _parse(self, url):
        while url:
            response = self._get_response(url)
            data = response.json()
            url = data["next"]
            for product in data["results"]:
                yield product

    def _save(self, data: dict, file_path: Path):
        file_path.write_text(json.dumps(data, ensure_ascii=False), encoding="UTF-8")


# Как вы и советовали отнаследовался от класса который был на вебинаре
class Parse5kaCategories(Parse5ka):
    def run(self):
        categories_url = "https://5ka.ru/api/v2/categories/"
        categories_resp = self._get_response(categories_url)
        for i in categories_resp.json():
            categories_path = self.save_path.joinpath(f'{i["parent_group_code"]}.json')
            product_list = []
            for product in self._parse(self.start_url + f'?categories={i["parent_group_code"]}'):
                product_list.append(product)
            if len(product_list) > 0:  # не создаю файл если в категории нет продуктов
                categories = {
                    "name": i["parent_group_name"],
                    "code": i["parent_group_code"],
                    "products": product_list,
                }
                self._save(categories, categories_path)


if __name__ == "__main__":
    url = "https://5ka.ru/api/v2/special_offers/"
    save_path = Path(__file__).parent.joinpath("categories")
    if not save_path.exists():
        save_path.mkdir()
    parser = Parse5kaCategories(url, save_path)
    parser.run()
