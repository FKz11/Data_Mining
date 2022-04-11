import re
from base64 import b64decode
import scrapy
from pymongo import MongoClient


class AutoyoulaSpider(scrapy.Spider):
    name = "autoyoula"
    allowed_domains = ["auto.youla.ru"]
    start_urls = ["https://auto.youla.ru/"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db_client = MongoClient()

    def _get_follow(self, response, selector_str, callback):
        for itm in response.css(selector_str):
            url = itm.attrib["href"]
            yield response.follow(url, callback=callback)

    def parse(self, response, *args, **kwargs):
        yield from self._get_follow(
            response,
            ".TransportMainFilters_brandsList__2tIkv .ColumnItemList_column__5gjdt a.blackLink",
            self.brand_parse,
        )

    def brand_parse(self, response):
        yield from self._get_follow(
            response, ".Paginator_block__2XAPy a.Paginator_button__u1e7D", self.brand_parse
        )
        yield from self._get_follow(
            response,
            "article.SerpSnippet_snippet__3O1t2 a.SerpSnippet_name__3F7Yu.blackLink",
            self.car_parse,
        )

    def _parameters_parse(self, response):
        parameters = {}
        for parameter in response.css(".AdvertSpecs_row__ljPcX"):
            name = parameter.css(".AdvertSpecs_label__2JHnS::text").extract_first()
            if parameter.css(".AdvertSpecs_data__xK2Qx a.blackLink::text").extract_first() is not None:
                parameters[name] = parameter.css(".AdvertSpecs_data__xK2Qx a.blackLink::text").extract_first()
            else:
                parameters[name] = parameter.css(".AdvertSpecs_data__xK2Qx::text").extract_first()
        return parameters

    @staticmethod
    def get_author_user_id(resp):
        marker = "window.transitState = decodeURIComponent"
        for script in resp.css("script"):
            try:
                if marker in script.css("::text").extract_first():
                    re_pattern = re.compile(r"youlaId%22%2C%22([a-zA-Z|\d]+)%22%2C%22avatar")
                    result = re.findall(re_pattern, script.css("::text").extract_first())
                    return (
                        resp.urljoin(f"/user/{result[0]}").replace("auto.", "", 1)
                        if result
                        else None
                    )
            except TypeError:
                pass

    @staticmethod
    def get_author_phone(resp):
        marker = "window.transitState = decodeURIComponent"
        for script in resp.css("script"):
            try:
                if marker in script.css("::text").extract_first():
                    re_pattern = re.compile(r"phone%22%2C%22([a-zA-Z|\d]+)Xw%3D%3D%22%2C%22time")
                    result = re.findall(re_pattern, script.css("::text").extract_first())
                    result = b64decode(b64decode(result[0])).decode('UTF-8')
                    return result
            except TypeError:
                pass

    def car_parse(self, response):
        data = {
            "url": response.url,
            "title": response.css(".AdvertCard_advertTitle__1S1Ak::text").extract_first(),
            "images": [img.attrib["src"] for img in response.css("img.PhotoGallery_photoImage__2mHGn")],
            "parameters": self._parameters_parse(response),
            "text": response.css(".AdvertCard_descriptionInner__KnuRi::text").extract_first(),
            "author_user_url": self.get_author_user_id(response),
            "phone": self.get_author_phone(response),
        }
        self.db_client["gb"][self.name].insert_one(data)
