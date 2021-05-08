from json import loads as json_loads
from html2text import html2text

from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose, Join


def get_description(script):
    description = html2text(json_loads(script)["description"])
    return description


def get_activity(string):
    activity = "".join(string).split(sep=', ')
    return activity


class VacancyLoader(ItemLoader):
    default_item_class = dict
    url_out = TakeFirst()
    title_in = Join("")
    title_out = TakeFirst()
    price_in = Join("")
    price_out = TakeFirst()
    description_in = MapCompose(get_description)
    description_out = TakeFirst()
    author_out = TakeFirst()


class AuthorLoader(ItemLoader):
    default_item_class = dict
    url_out = TakeFirst()
    title_in = Join("")
    title_out = TakeFirst()
    website_out = TakeFirst()
    activity_out = MapCompose(get_activity)
    description_in = Join("")
    description_out = TakeFirst()
