import json
from datetime import datetime
import scrapy


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://www.instagram.com/']
    login_url = 'https://www.instagram.com/accounts/login/ajax/'
    hash_followers = '5aefa9893005572d237da5068082d8d5'  # подписчики
    hash_following = '3dec7e2c57367ef3da3d987d89f9dbc8'  # подписки
    api_url = '/graphql/query/'

    header_var = {'include_reel': 'false',
                  'fetch_mutual': 'false',
                  'first': 24}

    def __init__(self, login, password, user1, user2, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.login = login
        self.password = password
        self.user1 = user1
        self.user2 = user2
        self.user1_id = None
        self.user2_id = None
        self.start_time = datetime.now()
        self.handshake = 0
        self.use_people = set()
        self.end = False
        self.getters_friends = set()
        self.followers = set()
        self.following = set()
        self.get_followers_end = False
        self.get_following_end = False

    def parse(self, response):
        try:
            js_data = self.js_data_extract(response)
            yield scrapy.FormRequest(
                self.login_url,
                method="POST",
                callback=self.parse,
                formdata={"username": self.login, "enc_password": self.password},
                headers={"X-CSRFToken": js_data["config"]["csrf_token"]},
            )
        except AttributeError:
            if response.json()["authenticated"]:
                yield response.follow(f"/{self.user1}/", callback=self.get_user1_id)

    def get_user1_id(self, response):
        js_data = self.js_data_extract(response)
        self.user1_id = js_data['entry_data']['ProfilePage'][0]['graphql']['user']['id']
        yield response.follow(f"/{self.user2}/", callback=self.get_user2_id)

    def get_user2_id(self, response):
        js_data = self.js_data_extract(response)
        self.user2_id = js_data['entry_data']['ProfilePage'][0]['graphql']['user']['id']
        return self.main_parse()

    def main_parse(self):
        friends = (self.getters_friends - self.use_people)
        self.getters_friends = set()
        for friend in friends:
            self.use_people.add(friend)
            if friend == self.user2_id:
                print(self.handshake)
                self.end = True
                break
        if not self.end:
            self.handshake += 1
            if len(self.use_people) == 0:
                return self.get_friends({self.user1_id})
            else:
                return self.get_friends(friends)

    def get_friends(self, friends):
        for friend in friends:
            self.header_var['id'] = friend
            yield scrapy.FormRequest(f"{self.start_urls[0]}"
                                     f"{self.api_url}?"
                                     f"query_hash={self.hash_followers}&"
                                     f"variables={json.dumps(self.header_var)}",
                                     callback=self.get_followers, )
            yield scrapy.FormRequest(f"{self.start_urls[0]}"
                                     f"{self.api_url}?"
                                     f"query_hash={self.hash_following}&"
                                     f"variables={json.dumps(self.header_var)}",
                                     callback=self.get_following, )

    def get_followers(self, response):
        for itm in response.json()['data']['user']['edge_followed_by']['edges']:
            self.followers.add(itm['node']['id'])
        end_cursor = response.json()['data']['user']['edge_followed_by']['page_info']['end_cursor']
        if end_cursor:
            header_var = self.header_var
            header_var["after"] = end_cursor
            yield scrapy.FormRequest(f"{self.start_urls[0]}"
                                     f"{self.api_url}?"
                                     f"query_hash={self.hash_followers}&"
                                     f"variables={json.dumps(header_var)}",
                                     callback=self.get_followers,)
        else:
            self.get_followers_end = True
            yield self.complete()

    def get_following(self, response):
        for itm in response.json()['data']['user']['edge_follow']['edges']:
            self.following.add(itm['node']['id'])
        end_cursor = response.json()['data']['user']['edge_follow']['page_info']['end_cursor']
        if end_cursor:
            header_var = self.header_var
            header_var["after"] = end_cursor
            yield scrapy.FormRequest(f"{self.start_urls[0]}"
                                     f"{self.api_url}?"
                                     f"query_hash={self.hash_following}&"
                                     f"variables={json.dumps(header_var)}",
                                     callback=self.get_following,)
        else:
            self.get_following_end = True
            yield self.complete()

    def complete(self):
        if self.get_followers_end and self.get_following_end:
            self.getters_friends.update(self.followers & self.following)
            self.followers = set()
            self.following = set()
            self.get_followers_end = False
            self.get_following_end = False
            return self.main_parse()

    def js_data_extract(self, response):
        script = response.xpath(
            "//script[contains(text(), 'window._sharedData = ')]/text()"
        ).extract_first()
        return json.loads(script.replace("window._sharedData = ", "")[:-1])
