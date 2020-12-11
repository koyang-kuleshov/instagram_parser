"""
Источник https://www.instagram.com
Создать паука который при запуске получает список имен идентификаторов
пользователей,

Обходит ленту постов пользователя,
собирает монго бд со след структурой:

user_name - имя пользвоателя
user_id - айдишник пользователя
data = data.user.edge_owner_to_timeline_media.edges[9].node
if edge_sidecar_to_children in data:
    data.edge_sidecar_to_children.edges[0].display_url
else:
    data.display_url
post_photos - все фото из поста
post_pub_date - дата публикации поста -- data.taken_at_timestamp
like_count - количество лайков поста -- data.edge_media_preview_like.count
Внимание, фото надо скачивать и сохранять, в бд надо хранить как ссылку на фото
так и путь куда сохранено фото
"""
import json
import re
from copy import deepcopy

import scrapy
from scrapy.loader import ItemLoader

from insta_parse.items import InstaParseItem


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['www.instagram.com']
    start_urls = ['https://www.instagram.com/']
    __login_url = 'https://www.instagram.com/accounts/login/ajax/'
    __api_url = '/graphql/query/'
    __api_query = 'bfa387b2992c3a52dcbe447467b4b771'
    variables = {"id": None, "first": 12}
    users = {}

    def __init__(self, login: str, passwd: str, parse_users: list,
                 *args, **kwargs):
        self.login = login
        self.passwd = passwd
        self.parse_users = parse_users
        super().__init__(*args, **kwargs)

    def parse(self, response):
        token = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(
            self.__login_url,
            method='POST',
            callback=self.im_login,
            formdata={
                'username': self.login,
                'enc_password': self.passwd,
            },
            headers={
                'X-CSRFToken': token
            }
        )

    def im_login(self, response):
        data = response.json()
        if data['authenticated']:
            for user_name in self.parse_users:
                yield response.follow(f'/{user_name}',
                                      callback=self.get_user_feed,
                                      cb_kwargs={'user': user_name}
                                      )

    def get_user_data(self, response, user_name):
        item = ItemLoader(InstaParseItem(), response)
        item.add_value('user_name', user_name)
        item.add_value('user_id', self.fetch_user_id(
            response.text,
            user_name
            )
        )
        item.add_value(self.get_user_feed(response, user_name))
        return item.load_item()

    def get_user_feed(self, response, user):
        user_id = self.fetch_user_id(response.text, user)
        user_vars = deepcopy(self.variables)
        user_vars.update({'id': user_id})
        yield response.follow(self.make_graphql_url(user_vars),
                              callback=self.parse_user_posts,
                              cb_kwargs={'user_vars': user_vars,
                                         'user': user}
                              )

    def parse_user_posts(self, response, user_vars, user):

        user_id = self.fetch_user_id(response.text, user)

        data = json.loads(response.body)
        json_posts = (data.get('data').get('user').
                      get('edge_owner_to_timeline_media').get('edges')
                      )
        for post in json_posts:
            item = ItemLoader(InstaParseItem(), response)
            item.add_value('user_name', user)
            item.add_value('user_id', user_id)
            item.add_value('post_pub_date', post.get('node').
                           get('taken_at_timestamp'))
            item.add_value('like_count', post.get('node').
                           get('edge_media_preview_like').
                           get('count')
                           )
            if (post.get('node').get('is_video') or
                    not post.get('node').get('edge_sidecar_to_children')):
                eggs = [{'src': post.get('node').get('display_resources')[2].
                         get('src')}]
            else:
                eggs = [{'src': photo.get('node').get('display_resources')[2].
                        get('src')} for photo in post.get('node').
                        get('edge_sidecar_to_children').get('edges')]
            item.add_value('post_photos', eggs)
            yield item.load_item()
        page_info = (data.get('data').get('user').
                     get('edge_owner_to_timeline_media').get('page_info')
                     )
        if page_info.get('has_next_page'):
            user_vars = deepcopy(self.variables)
            user_vars.update({'id': user_id})
            user_vars["after"] = page_info.get('end_cursor')
            yield response.follow(self.make_graphql_url(user_vars),
                                  callback=self.parse_user_posts,
                                  cb_kwargs={'user_vars': user_vars,
                                             'user': user}
                                  )

    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        token = matched.split(':').pop().replace(r'"', '')
        return token

    def fetch_user_id(self, text, username):
        """Используя регулярные выражения парсит переданную строку на наличие
        'id' нужного пользователя и возвращет его."""
        pattern = r'{\"id\":\"\d+\",\"username\":\"' + username + '\"}'
        matched = re.search(
            pattern,
            text
        ).group()
        return json.loads(matched).get('id')

    def make_graphql_url(self, user_vars):
        """Возвращает `url` для `graphql` запроса"""
        result = (f'{self.__api_url}?query_hash={self.__api_query}'
                  f'&variables={json.dumps(user_vars)}')
        return result
