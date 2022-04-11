import scrapy
from ..loaders import VacancyLoader, AuthorLoader
from ..xpath_selectors import xpath_selectors, xpath_vacancy_data_selectors, xpath_author_data_selectors


class HhSpider(scrapy.Spider):
    name = "hh"
    allowed_domains = ["hh.ru"]
    start_urls = ["https://hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113"]

    def _get_follow(self, response, selector_str, callback):
        for itm in response.xpath(selector_str):
            yield response.follow(itm, callback=callback)

    def parse(self, response, *args, **kwargs):
        yield from self._get_follow(
            response, xpath_selectors["pages"], self.parse
        )
        yield from self._get_follow(
            response, xpath_selectors["vacancy"], self.vacancy_parse,
        )

    def vacancy_parse(self, response):
        loader = VacancyLoader(response=response)
        loader.add_value("url", response.url)
        for key, xpath in xpath_vacancy_data_selectors.items():
            loader.add_xpath(key, xpath)
        yield loader.load_item()
        yield from self._get_follow(
            response, xpath_selectors["author"], self.author_parse,
        )

    def author_parse(self, response):
        loader = AuthorLoader(response=response)
        loader.add_value("url", response.url)
        for key, xpath in xpath_author_data_selectors.items():
            loader.add_xpath(key, xpath)
        yield loader.load_item()
