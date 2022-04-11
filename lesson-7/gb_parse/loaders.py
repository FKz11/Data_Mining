from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose


def get_tag_data(data):
    data_out = {}
    for key, value in data.items():
        if not (isinstance(value, dict) or isinstance(value, list)):
            data_out[key] = value
    return data_out


def get_post_data(data):
    data_out = {
        'id': data['id'],
        'shortcode': data['shortcode'],
        'owner': data['owner']['id'],
        'is_video': data['is_video'],
        'photo': None if data['is_video'] else data['thumbnail_resources'][-1]['src'],
        'meta': data
    }
    return data_out


class InstTagLoader(ItemLoader):
    default_item_class = dict
    date_parse_out = TakeFirst()
    data_in = MapCompose(get_tag_data)
    data_out = TakeFirst()


class InstPostLoader(ItemLoader):
    default_item_class = dict
    date_parse_out = TakeFirst()
    data_in = MapCompose(get_post_data)
    data_out = TakeFirst()
