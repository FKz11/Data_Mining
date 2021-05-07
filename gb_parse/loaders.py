from json import loads as json_loads
from html2text import html2text

from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose, Join


def get_description(script):
    description = html2text(json_loads(script)["description"])
    return description


def get_author(author):
    if len(author["title"]) != 0:
        author["title"] = "".join(author["title"])
    else:
        author["title"] = None
    if len(author["website"]) != 0:
        author["website"] = "".join(author["website"])
    else:
        author["website"] = None
    if len(author["activity"]) != 0:
        author["activity"] = "".join(author["activity"]).lower().split(sep=', ')
    else:
        author["activity"] = None
    return author


class HhLoader(ItemLoader):
    default_item_class = dict
    url_out = TakeFirst()
    title_out = TakeFirst()
    price_in = Join("")
    price_out = TakeFirst()
    description_in = MapCompose(get_description)
    description_out = TakeFirst()
    author_in = MapCompose(get_author)
    author_out = TakeFirst()
