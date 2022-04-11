"""
Источник https://www.avito.ru/krasnodar/kvartiry/prodam
Город можно сменить
задача обойти пагинацию и подразделы квартир в продаже.

Собрать данные:
URL
Title
Цена
Адрес (если доступен)
Параметры квартиры (блок под фото)
Ссылку на автора

Дополнительно но не обязательно вытащить телефон автора
"""

from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from gb_parse.spiders.avito import AvitoSpider

if __name__ == "__main__":
    crawler_settings = Settings()
    crawler_settings.setmodule("gb_parse.settings")
    crawler_process = CrawlerProcess(settings=crawler_settings)
    crawler_process.crawl(AvitoSpider)
    crawler_process.start()
