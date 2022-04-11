import scrapy
from ..loaders import AvitoLoader
from ..xpath_selectors import xpath_selectors, xpath_data_selectors


class AvitoSpider(scrapy.Spider):
    name = "avito"
    allowed_domains = ["www.avito.ru"]
    start_urls = ["https://www.avito.ru/moskva/kvartiry/prodam"]

    def _get_follow(self, response, selector_str, callback):
        for itm in response.xpath(selector_str):
            yield response.follow(itm, callback=callback)

    def parse(self, response, *args, **kwargs):
        yield from self._get_follow(
            response, xpath_selectors["pages"], self.parse
        )
        yield from self._get_follow(
            response, xpath_selectors["flat"], self.flat_parse,
        )

    def flat_parse(self, response):
        loader = AvitoLoader(response=response)
        loader.add_value("url", response.url)
        for key, xpath in xpath_data_selectors.items():
            loader.add_xpath(key, xpath)
        yield scrapy.Request("https://www.avito.ru/web/1/items/phone/" + response.url[-10:], callback=self.phone_parse,
                             meta={"loader": loader})

    def phone_parse(self, response):
        loader = response.meta["loader"]
        loader.add_value("phone", response.text)
        yield loader.load_item()
