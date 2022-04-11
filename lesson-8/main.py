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
    user1 = "7.onov"
    user2 = "kiril_live"
    crawler_process.crawl(
        InstagramSpider,
        login=os.getenv("INST_LOGIN"),
        password=os.getenv("INST_PSWORD"),
        user1=user1,
        user2=user2,
    )
    crawler_process.start()
