"""
Источник instgram.
Авторизованным пользователем обходит список произвольных тегов.
Сохраняет структуру Item олицетворяющую сам Tag (только информация о теге).
Сохраняет структуру данных поста, включая обход пагинации.
Все структуры имеют следующий вид:
date_parse (datetime) - время когда произошло создание структуры
data - данные полученые от instgram
Скачивает изображения всех постов и сохраняет их на диск

Файл .env:
INST_LOGIN=******@yandex.ru
INST_PSWORD=#PWD_INSTAGRAM_BROWSER*********************************************************
"""

import os
import dotenv
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from gb_parse.spiders.instagram import InstagramSpider

if __name__ == "__main__":
    dotenv.load_dotenv(".env")
    crawler_settings = Settings()
    crawler_settings.setmodule("gb_parse.settings")
    crawler_process = CrawlerProcess(settings=crawler_settings)
    tags = ["python", "data", "mining"]
    crawler_process.crawl(
        InstagramSpider,
        login=os.getenv("INST_LOGIN"),
        password=os.getenv("INST_PSWORD"),
        tags=tags,
    )
    crawler_process.start()
