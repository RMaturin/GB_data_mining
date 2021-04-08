from scrapy.loader import ItemLoader
from scrapy import Selector
from itemloaders.processors import TakeFirst, MapCompose
from .items import GbAutoYoulaItem

from urllib.parse import urljoin
from base64 import b64decode


def get_characteristics(item):
    selector = Selector(text=item)
    data = {
        "name": selector.xpath(
            "//div[contains(@class, 'AdvertSpecs_label')]/text()"
        ).extract_first(),
        "value": selector.xpath(
            "//div[contains(@class, 'AdvertSpecs_data')]//text()"
        ).extract_first(),
    }
    return data


def create_user_url(user_id):
    return urljoin("https://youla.ru/user/", user_id)


def clear_price(price: str) -> float:
    try:
        return float(price.replace("\u2009", ""))
    except ValueError:
        return float("NaN")


def decode_phone(phone):
    return b64decode(b64decode(f"{phone}==")).decode("utf-8")


class AutoYoulaLoder(ItemLoader):
    default_item_class = GbAutoYoulaItem
    url_out = TakeFirst()
    title_out = TakeFirst()
    characteristics_in = MapCompose(get_characteristics)
    author_in = MapCompose(create_user_url)
    author_out = TakeFirst()
    price_in = MapCompose(clear_price)
    price_out = TakeFirst()
    descriptions_out = TakeFirst()
    phone_in = MapCompose(decode_phone)
    phone_out = TakeFirst()
