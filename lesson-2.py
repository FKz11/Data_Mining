"""
Источник https://gb.ru/posts/
Необходимо обойти все записи в блоге и извлеч из них информацию следующих полей:
url страницы материала
Заголовок материала
Первое изображение материала (Ссылка)
Дата публикации (в формате datetime)
имя автора материала
ссылка на страницу автора материала
комментарии в виде (автор комментария и текст комментария)
Структуру сохраняем в MongoDB
"""


import time
import datetime
import typing

import requests
from urllib.parse import urljoin
from pymongo import MongoClient
import bs4


class GbBlogParse:
    def __init__(self, start_url, collection):
        self.time = time.time()
        self.start_url = start_url
        self.collection = collection
        self.done_urls = set()
        self.tasks = []
        start_task = self.get_task(self.start_url, self.parse_feed)
        self.tasks.append(start_task)
        self.done_urls.add(self.start_url)

    def _get_response(self, url, *args, **kwargs):
        if self.time + 0.9 < time.time():
            time.sleep(0.5)
        response = requests.get(url, *args, **kwargs)
        self.time = time.time()
        print(url)
        return response

    def _get_soup(self, url, *args, **kwargs):
        soup = bs4.BeautifulSoup(self._get_response(url, *args, **kwargs).text, "lxml")
        return soup

    def get_task(self, url: str, callback: typing.Callable) -> typing.Callable:
        def task():
            soup = self._get_soup(url)
            return callback(url, soup)

        if url in self.done_urls:
            return lambda *_, **__: None
        self.done_urls.add(url)
        return task

    def task_creator(self, url, tags_list, callback):
        links = set(
            urljoin(url, itm.attrs.get("href"))
            for itm in tags_list
            if itm.attrs.get("href")
        )
        for link in links:
            task = self.get_task(link, callback)
            self.tasks.append(task)

    def parse_comments(self, commentable_id):
        url_comments = "https://gb.ru/api/v2/comments?commentable_type=Post&order=desc&commentable_id=" + commentable_id
        comments = []
        children_comments = [self._get_response(url_comments).json()]
        for children_comments_json in children_comments:
            for children_comment in children_comments_json:
                comments.append({"Full name": children_comment["comment"]["user"]["full_name"],
                                 "User url": children_comment["comment"]["user"]["url"],
                                 "Text": children_comment["comment"]["body"]})
                if children_comment["comment"]["children"]:
                    children_comments.append(children_comment["comment"]["children"])
        return comments

    def parse_feed(self, url, soup):
        ul_pagination = soup.find("ul", attrs={"class": "gb__pagination"})
        self.task_creator(url, ul_pagination.find_all("a"), self.parse_feed)
        post_wrapper = soup.find("div", attrs={"class": "post-items-wrapper"})
        self.task_creator(
            url, post_wrapper.find_all("a", attrs={"class": "post-item__title"}), self.parse_post
        )

    def parse_post(self, url, soup):
        title_tag = soup.find("h1", attrs={"class": "blogpost-title"})
        first_image_url = soup.find("img")
        date_time = soup.find("time", attrs={"itemprop": "datePublished"})
        author_name = soup.find(attrs={"itemprop": "author"})
        author_url = author_name.parent.get("href")
        comments = self.parse_comments(soup.find("comments").get("commentable-id"))
        data = {
            "url": url,
            "title": title_tag.text,
            "first_image_url": first_image_url.get("src"),
            "date_time": datetime.datetime.strptime(date_time.get("datetime"), "%Y-%m-%dT%H:%M:%S%z"),
            "author_name": author_name.text,
            "author_url": urljoin("https://gb.ru", author_url),
            "comments": comments,
        }
        return data

    def run(self):
        for task in self.tasks:
            task_result = task()
            if isinstance(task_result, dict):
                self.save(task_result)

    def save(self, data):
        self.collection.insert_one(data)


if __name__ == "__main__":
    collection = MongoClient()["gb"]["gb_posts"]
    parser = GbBlogParse("https://gb.ru/posts", collection)
    parser.run()