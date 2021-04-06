from scrapy.loader import ItemLoader
from .items import GbAutoYoulaItem


class AutoYoulaLoder(ItemLoader):
    default_item_class = GbAutoYoulaItem
