import scrapy
from ..loaders import HhLoader


class HhSpider(scrapy.Spider):
    name = "hh"
    allowed_domains = ["hh.ru"]
    start_urls = ["https://hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113"]

    _xpath_selectors = {
        "pages": '//a[@data-qa="pager-next"]/@href',
        "vacancy": '//a[@data-qa="vacancy-serp__vacancy-title"]/@href',
        "author": '//a[@data-qa="vacancy-company-name"]/@href'
    }

    _xpath_vacancy_data_selectors = {
        "title": "//h1//text()",
        "price": "//p[@class='vacancy-salary']/span/text()",
        "description": "//script[@type='application/ld+json']/text()",
        "tags": "//span[@data-qa='bloko-tag__text']/text()",
    }

    _xpath_author_data_selectors = {
        "title": "//div[@class='company-header']//h1//text()",
        "website": "//a[@data-qa='sidebar-company-site']/@href",
        "activity": "//div[@class='employer-sidebar-block']/p/text()",
        "vacancies": "//a[@data-qa='vacancy-serp__vacancy-title']/@href",
    }

    def _get_follow(self, response, selector_str, callback):
        for itm in response.xpath(selector_str):
            yield response.follow(itm, callback=callback)

    def parse(self, response, *args, **kwargs):
        yield from self._get_follow(
            response, self._xpath_selectors["pages"], self.parse
        )
        yield from self._get_follow(
            response, self._xpath_selectors["vacancy"], self.vacancy_parse,
        )

    def vacancy_parse(self, response):
        loader = HhLoader(response=response)
        loader.add_value("url", response.url)
        for key, xpath in self._xpath_vacancy_data_selectors.items():
            loader.add_xpath(key, xpath)
        if response.xpath(self._xpath_selectors["author"]).get() is not None:
            yield scrapy.Request("https://hh.ru" + response.xpath(self._xpath_selectors["author"]).get(),
                                 meta={'loader': loader}, callback=self.author_parse)

    def author_parse(self, response):
        loader = response.meta["loader"]
        author = {"url": response.url}
        author.update({key: response.xpath(xpath).getall() for key, xpath in self._xpath_author_data_selectors.items()})
        loader.add_value("author", author)
        yield loader.load_item()
