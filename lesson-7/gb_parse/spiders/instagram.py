import json
from datetime import datetime
import scrapy
from ..items import InstaTag, InstaPost
from ..loaders import InstTagLoader, InstPostLoader


class InstagramSpider(scrapy.Spider):
    name = "instagram"
    allowed_domains = ["www.instagram.com"]
    start_urls = ["https://www.instagram.com/"]
    _login_url = "https://www.instagram.com/accounts/login/ajax/"
    _tags_path = "/explore/tags/"
    api_url = "/graphql/query/"
    query_hash = "9b498c08113f1e09617a1703c22b2f32"

    def __init__(self, login, password, tags, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.login = login
        self.password = password
        self.tags = tags

    def parse(self, response):
        try:
            js_data = self.js_data_extract(response)
            yield scrapy.FormRequest(
                self._login_url,
                method="POST",
                callback=self.parse,
                formdata={"username": self.login, "enc_password": self.password},
                headers={"X-CSRFToken": js_data["config"]["csrf_token"]},
            )
        except AttributeError:
            if response.json()["authenticated"]:
                for tag in self.tags:
                    yield response.follow(f"{self._tags_path}{tag}/", callback=self.tag_page_parse)

    def tag_page_parse(self, response):
        js_data = self.js_data_extract(response)
        hashtag = js_data['entry_data']['TagPage'][0]['graphql']['hashtag']
        yield from self.load_tag_item(hashtag)
        yield from self.load_post_items(hashtag)
        yield response.follow(
            f"{self.api_url}?query_hash={self.query_hash}&variables={json.dumps(self.get_header_var(hashtag))}",
            callback=self.pagination_parse)

    def load_tag_item(self, hashtag):
        tag_item = InstaTag()
        tag_loader = InstTagLoader(tag_item)
        tag_loader.add_value('date_parse', datetime.utcnow())
        tag_loader.add_value('data', hashtag)
        yield tag_loader.load_item()

    def load_post_items(self, hashtag):
        for edge in hashtag['edge_hashtag_to_media']['edges']:
            post_item = InstaPost()
            post_loader = InstPostLoader(post_item)
            post_loader.add_value("date_parse", datetime.utcnow())
            post_loader.add_value("data", edge["node"])
            yield post_loader.load_item()

    def get_header_var(self, hashtag):
        header_var = {
            "tag_name": hashtag["name"],
            "first": 100,
            "after": hashtag["edge_hashtag_to_media"]["page_info"]["end_cursor"]}
        return header_var

    def pagination_parse(self, response):
        hashtag = response.json()["data"]["hashtag"]
        yield from self.load_post_items(hashtag)
        yield response.follow(
            f"{self.api_url}?query_hash={self.query_hash}&variables={json.dumps(self.get_header_var(hashtag))}",
            callback=self.pagination_parse)

    def js_data_extract(self, response):
        script = response.xpath(
            "//script[contains(text(), 'window._sharedData = ')]/text()"
        ).extract_first()
        return json.loads(script.replace("window._sharedData = ", "")[:-1])
