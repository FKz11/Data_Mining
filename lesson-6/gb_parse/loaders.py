from json import loads as json_loads
from base64 import b64decode
from io import BytesIO
from PIL import Image

from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose, Compose

import pytesseract

# Из за труднсотей скачивал руками отсюда: https://github.com/UB-Mannheim/tesseract/wiki
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def get_price(data):
    price = data + " ₽"
    return price


def get_address(data):
    address = data.replace("\n ", "")
    return address


def get_parameters(data):
    parameters_list_no_proc = [itm.replace(":", "") for itm in data if (itm != " ") and (itm != "\n  ")]
    parameters_list = [itm[:-1] if itm[-1] == " " else itm for itm in parameters_list_no_proc]
    parameters_dict = dict(zip(parameters_list[::2], parameters_list[1::2]))
    return parameters_dict


def get_author(data):
    author = "https://www.avito.ru" + data
    return author


def get_phone(data):
    phone_string = json_loads(data)["image64"].split(sep=',')[1]
    image = Image.open(BytesIO(b64decode(phone_string)))
    phone = pytesseract.image_to_string(image).replace("\n", "")
    return phone


class AvitoLoader(ItemLoader):
    default_item_class = dict
    url_out = TakeFirst()
    title_out = TakeFirst()
    price_in = MapCompose(get_price)
    price_out = TakeFirst()
    address_in = MapCompose(get_address)
    address_out = TakeFirst()
    parameters_out = Compose(get_parameters)
    author_in = MapCompose(get_author)
    author_out = TakeFirst()
    phone_in = MapCompose(get_phone)
    phone_out = TakeFirst()
