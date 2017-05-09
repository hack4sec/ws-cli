# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Unit tests for SpiderResult
"""

import re

import pytest

from Common import Common
from classes.SpiderResult import SpiderResult
from classes.Registry import Registry


class Test_SpiderResult(Common):
    """Unit tests for SpiderResult"""
    model = None

    def setup(self):
        self.db.q("TRUNCATE TABLE urls")
        self.db.q("TRUNCATE TABLE urls_base")
        self.db.q("TRUNCATE TABLE `hosts`")
        self.db.q("TRUNCATE TABLE `ips`")
        self.db.q("TRUNCATE TABLE `projects`")

        Registry().get('mongo').spider_urls.drop()

        self.model = SpiderResult()

        Registry().set('allow_regexp', re.compile(''))
        Registry().get('mongo').spider_urls.create_index([('hash', 1)], unique=True, dropDups=True)
        Registry().get('mongo').spider_urls.create_index([('checked', 1)])

    codes_stat_data = [
        (
            [
                {'hash': '1', 'path': '/1', 'query': 'a', 'code': 200, },
                {'hash': '2', 'path': '/2', 'query': 'b', 'code': 301, },
                {'hash': '3', 'path': '/3', 'query': 'c', 'code': 404, },
            ],
            {200: [u'/1?a'], 301: [u'/2?b'], 404: [u'/3?c']}
        ),
        (
            [
                {'hash': '1', 'path': '/1', 'query': 'a', 'code': 200, },
                {'hash': '2', 'path': '/1', 'query': 'aa', 'code': 200, },
                {'hash': '3', 'path': '/1', 'query': 'aaa', 'code': 200, },
                {'hash': '4', 'path': '/2', 'query': 'b', 'code': 301, },
                {'hash': '5', 'path': '/3', 'query': 'c', 'code': 404, },
            ],
            {200: [u'/1?a', u'/1?aa', u'/1?aaa'], 301: [u'/2?b'], 404: [u'/3?c']}
        ),
    ]

    @pytest.mark.parametrize("urls_to_db,expected_data", codes_stat_data)
    def test_get_codes_stat(self, urls_to_db, expected_data):
        Registry().get('mongo').spider_urls.insert(urls_to_db)
        assert self.model._get_codes_stat() == expected_data

    def test_get_slowest_links(self):
        urls_data = [
            {'hash': '1', 'path': '/1', 'query': 'a', 'code': 200, 'time': 0},
            {'hash': '2', 'path': '/2', 'query': 'b', 'code': 301, 'time': 1, },
            {'hash': '3', 'path': '/3', 'query': 'c', 'code': 404, 'time': 2, },
        ]
        Registry().get('mongo').spider_urls.insert(urls_data)

        check_data = [
            {u'code': 404, u'time': 2, 'url': u'/3?c'},
            {u'code': 301, u'time': 1, 'url': u'/2?b'},
            {u'code': 200, u'time': 0, 'url': u'/1?a'}
        ]
        assert self.model._get_slowest_links() == check_data

    def test_get_extensions(self):
        urls_data = [
            {'hash': '1', 'path': '/1.php', 'query': 'a', 'code': 200, 'time': 0},
            {'hash': '2', 'path': '/2.php', 'query': 'b', 'code': 301, 'time': 1, },
            {'hash': '3', 'path': '/3.txt', 'query': 'c', 'code': 404, 'time': 2, },
        ]
        Registry().get('mongo').spider_urls.insert(urls_data)

        check_data = {
            u'.php': [u'/1.php?a', u'/2.php?b'],
            u'.txt': [u'/3.txt?c']
        }
        assert self.model._get_extensions() == check_data
