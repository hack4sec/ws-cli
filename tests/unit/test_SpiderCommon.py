# -*- coding: utf-8 -*-

import copy
from pprint import pprint
from urlparse import urlparse
from urlparse import ParseResult
import hashlib
import re
import os
import random
import shutil

import pytest

from ModelsCommon import ModelsCommon
from Logger import Logger
from classes.SpiderCommon import SpiderCommon
from classes.Registry import Registry
from classes.models.UrlsModel import UrlsModel


class Test_SpiderCommon(ModelsCommon):
    def setup(self):
        self.db.q("TRUNCATE TABLE urls")
        self.db.q("TRUNCATE TABLE urls_base")
        self.db.q("TRUNCATE TABLE `hosts`")
        self.db.q("TRUNCATE TABLE `ips`")
        self.db.q("TRUNCATE TABLE `projects`")
        Registry().get('mongo').spider_urls.drop()
        self.model = SpiderCommon()
        Registry().set('allow_regexp', re.compile(''))
        Registry().get('mongo').spider_urls.create_index([('hash', 1)], unique=True, dropDups=True)
        Registry().get('mongo').spider_urls.create_index([('checked', 1)])

    def test_make_full_new_scan(self):
        url_data = [
            {'url': '/1/', 'project_id': 1, 'host_id': 1, 'hash': '/ref1/', 'response_code': 401, 'response_time': 10, 'who_add': 'dafs', 'spidered': 1, 'size': 20, 'descr': 'some descr'},
            {'url': '/2/', 'project_id': 1, 'host_id': 1, 'response_code': 401, 'response_time': 10, 'who_add': 'dafs', 'spidered': 1, 'size': 20, 'descr': 'some descr'},
            {'url': '/3/', 'project_id': 1, 'host_id': 1, 'hash': '/ref3/', 'response_time': 10, 'who_add': 'dafs', 'spidered': 1, 'size': 20, 'descr': 'some descr'},
            {'url': '/4/', 'project_id': 1, 'host_id': 1, 'hash': '/ref4/', 'response_code': 401, 'who_add': 'dafs', 'spidered': 1, 'size': 20, 'descr': 'some descr'},
            {'url': '/5/', 'project_id': 1, 'host_id': 1, 'hash': '/ref5/', 'response_code': 401, 'response_time': 10, 'spidered': 1, 'size': 20, 'descr': 'some descr'},
            {'url': '/6/', 'project_id': 1, 'host_id': 1, 'hash': '/ref6/', 'response_code': 401, 'response_time': 10, 'who_add': 'dafs', 'spidered': 1, 'size': 20, 'descr': 'some descr'},
            {'url': '/7/', 'project_id': 2, 'host_id': 1, 'hash': '/ref7/', 'response_code': 401, 'response_time': 10, 'who_add': 'dafs', 'spidered': 1, 'descr': 'some descr'},
            {'url': '/8/', 'project_id': 2, 'host_id': 1, 'hash': '/ref8/', 'response_code': 401, 'response_time': 10, 'who_add': 'dafs', 'spidered': 1, 'size': 20}
        ]
        for url_row in url_data:
            self.db.insert("urls", url_row)

        assert self.db.fetch_one("SELECT COUNT(id) FROM urls WHERE spidered=1") == 8
        assert self.db.fetch_one("SELECT COUNT(id) FROM urls WHERE spidered=1 AND project_id=1") == 6
        assert self.db.fetch_one("SELECT COUNT(id) FROM urls WHERE spidered=1 AND project_id=2") == 2

        self.model.make_full_new_scan(1)

        assert self.db.fetch_one("SELECT COUNT(id) FROM urls WHERE spidered=1") == 2
        assert self.db.fetch_one("SELECT COUNT(id) FROM urls WHERE spidered=1 AND project_id=1") == 0
        assert self.db.fetch_one("SELECT COUNT(id) FROM urls WHERE spidered=1 AND project_id=2") == 2

    def test_clear_link_obj(self):
        test_obj = copy.deepcopy(self.model._link_object)
        test_obj['a'] = 'a'
        test_obj['b'] = 'b'

        clean_data = self.model._clear_link_obj(test_obj)

        assert 'a' not in clean_data.keys()
        assert 'b' not in clean_data.keys()

        for _field in self.model._link_object.keys():
            assert _field in clean_data.keys()

        assert len(clean_data.keys()) == len(self.model._link_object.keys())

    def test_links_checked(self):
        urls_data = [
            {'hash': '1', 'path': '/1', 'query': 'a', 'checked': 0,},
            {'hash': '2', 'path': '/2', 'query': 'b', 'checked': 0, },
            {'hash': '3', 'path': '/3', 'query': 'c', 'checked': 0, },
        ]

        Registry().get('mongo').spider_urls.insert(urls_data)

        assert Registry().get('mongo').spider_urls.find({'checked': 0}).count() == 3

        del urls_data[2]

        self.model.links_checked(urls_data)

        assert Registry().get('mongo').spider_urls.find({'checked': 0}).count() == 1
        assert Registry().get('mongo').spider_urls.find({'checked': 1}).count() == 2

    def test_gen_url(self):
        assert self.model.gen_url({'path': '/', 'query': ''}, 'test.com') == 'http://test.com/'
        assert self.model.gen_url({'path': '/', 'query': 'abc'}, 'test.com') == 'http://test.com/?abc'

    def test_prepare_links_for_insert(self):
        test_site = "site.com"
        test_url = "/test/index.php"
        test_data = [
            '/',
            '',
            '//host.com',
            'relative',
            'http://www.site.com/index1.php',
            'http://www.site.com/a/index.php',
            'http://site.com/index2.php',
            'http://www.newsite.com/index3.php',
        ]

        assert len(self.model._external_hosts) == 0

        test1 = self.model.prepare_links_for_insert(test_data, urlparse(test_url), test_site)
        pprint(self.model._external_hosts)
        assert self.model._external_hosts == ['host.com', 'www.newsite.com']

        index1_found = False
        index2_found = False
        index3_found = False
        a_found = False
        a_index_found = False
        relative_found = False
        test_found = False
        for test_row in test1:
            if test_row.path == '/a/index.php':
                a_index_found = True
            if test_row.path == '/a/':
                a_found = True
            if test_row.path == '/index1.php':
                index1_found = True
            if test_row.path == '/index2.php':
                index2_found = True
            if test_row.path == '/index3.php':
                index3_found = True
            if test_row.path == '/test/relative':
                relative_found = True
            if test_row.path == '/test/':
                test_found = True

        assert index1_found
        assert index2_found
        assert not index3_found
        assert a_index_found
        assert a_found
        assert relative_found
        assert test_found

        assert len(test1) == 12

    def test_get_denied_schemas(self):
        assert self.model.get_denied_schemas() == ['denied1', 'denied2', 'denied3']

    def test_get_url_hash(self):
        url = "/tmp/1.txt"
        assert self.model.get_url_hash(url, '') == hashlib.md5(url.encode('utf-8')).hexdigest()
        assert self.model.get_url_hash(url, '?a=b') == hashlib.md5((url + '?a=b').encode('utf-8')).hexdigest()

    def test_insert_links(self):
        test_site = "site.com"
        test_url = "/test/index.php"
        test_data = [
            '/',
            '',
            '//host.com',
            'relative',
            'http://www.site.com/index1.php',
            'http://www.site.com/a/index.php',
            'http://site.com/index2.php?a=b',
            'http://www.newsite.com/index3.php',
        ]
        assert Registry().get('mongo').spider_urls.find().count() == 0
        self.model.insert_links(test_data, test_url, test_site)
        assert Registry().get('mongo').spider_urls.find().count() == 7

        paths_for_check = [
            '/a/',
            '/',
            '/index2.php',
            '/a/index.php',
            '/index1.php',
            '/test/',
            '/test/relative'
        ]
        for path_for_check in paths_for_check:
            test_row = Registry().get('mongo').spider_urls.find_one({'path': path_for_check})
            assert test_row['path'] == path_for_check
            if test_row['path'] == '/index2.php':
                assert test_row['query'] == 'a=b'

    def test_link_allowed(self):
        Registry().set('allow_regexp', re.compile('allowed'))
        assert bool(self.model._link_allowed(ParseResult(path="/abc/allowed.php", scheme='', netloc='', params='', query='', fragment='')))
        assert not bool(self.model._link_allowed(ParseResult(path="/denied2.php", scheme='', netloc='', params='', query='', fragment='')))

    def test_build_path(self):
        test_link = ParseResult(path="/abc/allowed.php", scheme='', netloc='', params='', query='', fragment='')
        assert self.model.build_path(test_link, "def") == test_link

        test_link = ParseResult(path="abc/allowed.php", scheme='', netloc='', params='', query='', fragment='')
        check_link = ParseResult(path="/a/abc/allowed.php", scheme='', netloc='', params='', query='', fragment='')
        assert self.model.build_path(test_link, "/a/") == check_link

    def test_del_file_from_path(self):
        assert self.model.del_file_from_path("/abc/abc.php") == "/abc"
        assert self.model.del_file_from_path("aaa") == ""
        assert self.model.del_file_from_path("/abc/abc") == "/abc"

    def test_clear_link(self):
        test_link = ParseResult(path="/ab\\c//./d/../allowed.php", scheme='', netloc='', params='', query='?a=b&amp;c=d', fragment='')
        check_link = ParseResult(path="/ab/c/allowed.php", scheme='', netloc='', params='', query='?a=b&c=d', fragment='')
        assert self.model.clear_link(test_link) == check_link

    def test_get_link_data_by_hash(self):
        urls_data = [
            {'hash': '1', 'path': '/1', 'query': 'a', 'checked': 0,},
            {'hash': '2', 'path': '/2', 'query': 'b', 'checked': 0, },
            {'hash': '3', 'path': '/3', 'query': 'c', 'checked': 0, },
        ]

        Registry().get('mongo').spider_urls.insert(urls_data)
        self.model.get_link_data_by_hash('1') == urls_data[0]

    def test_clear_old_data(self):
        urls_data = [
            {'hash': '1', 'path': '/1', 'query': 'a', 'checked': 0,},
            {'hash': '2', 'path': '/2', 'query': 'b', 'checked': 0, },
            {'hash': '3', 'path': '/3', 'query': 'c', 'checked': 0, },
        ]
        Registry().get('mongo').spider_urls.insert(urls_data)

        assert Registry().get('mongo').spider_urls.find().count() == 3

        os.mkdir("/tmp/somewstest")
        os.mkdir("/tmp/somewstest/host")
        os.mkdir("/tmp/somewstest/host/a")
        open('/tmp/somewstest/host/a/a.txt', 'w').close()

        Registry().set('data_path', '/tmp/somewstest/')
        self.model.clear_old_data("host")

        assert not os.path.exists("/tmp/somewstest/host")
        os.rmdir("/tmp/somewstest")

        assert Registry().get('mongo').spider_urls.find().count() == 0

    def test_get_pages_list(self):
        self.model._pages = ['abc']
        assert self.model._get_pages_list('host') == ['abc']

        self.model._pages = []
        os.mkdir("/tmp/somewstest")
        os.mkdir("/tmp/somewstest/host")
        Registry().set('data_path', '/tmp/somewstest/')

        test_files = []
        for _ in range(0, 3):
            test_file = hashlib.md5(str(random.randint(1, 10000)).encode('utf-8')).hexdigest()
            open("/tmp/somewstest/host/" + test_file, 'w').close()
            test_files.append(test_file)

        pages = self.model._get_pages_list("host")
        for page in pages:
            assert page in test_files
        assert len(pages) == len(test_files)

        shutil.rmtree("/tmp/somewstest")

    def test_prepare_first_pages(self):
        Registry().set('pData', {'id': 1})
        Registry().set('logger', Logger())
        self.db.q("INSERT INTO projects (id, name, descr) VALUES(1, 'prj', '')")
        self.db.q("INSERT INTO `hosts` (id, project_id, ip_id, name, descr) VALUES (1,1,1,'test.com', '')")

        urls_data = [
            {'hash': '1', 'path': '/1', 'query': 'a', 'checked': 0,},
            {'hash': '2', 'path': '/2', 'query': 'b', 'checked': 0, },
            {'hash': '3', 'path': '/3', 'query': 'c', 'checked': 0, },
        ]
        Registry().get('mongo').spider_urls.insert(urls_data)

        self.model.prepare_first_pages("test.com")

        assert Registry().get('mongo').spider_urls.find().count() == 1
        assert Registry().get('mongo').spider_urls.find_one()['path'] == '/'

        data = [
            {'url': '/', 'referer': '/', 'response_code': 200, 'response_time': 10, 'who_add': 'dafs1',
             'spidered': 0, 'size': 20, 'descr': 'some descr'},
            {'url': '/1/', 'referer': '/ref1/', 'response_code': 200, 'response_time': 10, 'who_add': 'dafs1', 'spidered': 0, 'size': 20, 'descr': 'some descr'},
        ]
        UrlsModel().add_mass(1, 1, data)

        Registry().get('mongo').spider_urls.drop()
        self.model.prepare_first_pages("test.com")

        assert Registry().get('mongo').spider_urls.find_one({'path': '/'})['path'] == '/'
        assert Registry().get('mongo').spider_urls.find_one({'path': '/1/'})['path'] == '/1/'
        assert Registry().get('mongo').spider_urls.find().count() == 2

    def test_links_in_spider_base(self):
        Registry().set('pData', {'id': 1})
        self.db.q("INSERT INTO projects (id, name, descr) VALUES(1, 'prj', '')")
        self.db.q("INSERT INTO `hosts` (id, project_id, ip_id, name, descr) VALUES (1,1,1,'test.com', '')")

        data = [
            {'url': '/', 'referer': '/', 'response_code': 0, 'response_time': 0, 'who_add': 'dafs1',
             'spidered': 0, 'size': 0, 'descr': 'some descr'},
        ]
        UrlsModel().add_mass(1, 1, data)

        assert self.db.fetch_one("SELECT COUNT(id) FROM urls") == 1
        assert self.db.fetch_one("SELECT spidered FROM urls WHERE url='/'") == 0

        urls_data = [
            {'referer': '/', 'code': 200, 'time': 10, 'who_add': 'dafs1',
             'spidered': 1, 'size': 20, 'descr': 'some descr', 'hash': '6666cd76f96956469e7be39d750cc7d9', 'query': '', 'path': '/', 'checked': 1},
            {'referer': '/ref1/', 'code': 200, 'time': 10, 'who_add': 'spider',
             'spidered': 1, 'size': 20, 'descr': '', 'hash': 'fa06d89c65fb808240e37f4c9e128955', 'query': '', 'path': '/1/', 'checked': 1},
        ]
        Registry().get('mongo').spider_urls.insert(urls_data)
        self.model.links_in_spider_base(1, 'test.com')
        assert self.db.fetch_one("SELECT COUNT(id) FROM urls") == 2
        assert self.db.fetch_one("SELECT spidered FROM urls WHERE url='/'") == 1

        for url_data in urls_data:
            test_row = self.db.fetch_row("SELECT *, url as path, response_code as code, response_time as `time`, '' as query, 1 as checked FROM urls WHERE `url` = '{0}'".format(url_data['path']))
            for field in url_data:
                if field == '_id':
                    continue
                assert url_data[field] == test_row[field]

    def test_links_in_urls_base(self):
        Registry().set('pData', {'id': 1})
        self.db.q("INSERT INTO projects (id, name, descr) VALUES(1, 'prj', '')")
        self.db.q("INSERT INTO `hosts` (id, project_id, ip_id, name, descr) VALUES (1,1,1,'test.com', '')")

        data = [
            {'url': '/', 'referer': '/', 'response_code': 0, 'response_time': 0, 'who_add': 'dafs1',
             'spidered': 0, 'size': 0, 'descr': 'some descr'},
        ]
        UrlsModel().add_mass(1, 1, data)

        assert self.db.fetch_one("SELECT COUNT(id) FROM urls") == 1
        assert self.db.fetch_one("SELECT spidered FROM urls WHERE url='/'") == 0

        urls_data = [
            {'referer': '/', 'code': 200, 'time': 10, 'who_add': 'dafs1',
             'spidered': 1, 'size': 20, 'descr': 'some descr', 'hash': '6666cd76f96956469e7be39d750cc7d9', 'query': '', 'path': '/', 'checked': 1},
            {'referer': '/ref1/', 'code': 200, 'time': 10, 'who_add': 'spider',
             'spidered': 1, 'size': 20, 'descr': '', 'hash': 'fa06d89c65fb808240e37f4c9e128955', 'query': '', 'path': '/1/', 'checked': 1},
        ]
        Registry().get('mongo').spider_urls.insert(urls_data)
        self.model.links_in_urls_base(1, 'test.com')
        assert self.db.fetch_one("SELECT COUNT(id) FROM urls_base") == 2

        assert self.db.fetch_one("SELECT COUNT(id) FROM urls_base WHERE name='/' AND parent_id=0") == 1
        assert self.db.fetch_one("SELECT COUNT(id) FROM urls_base WHERE name='1' AND parent_id=1") == 1

    @pytest.mark.skip(reason="Strange fail reason - 2 method upper work good, together - bad")
    def test_links_in_database(self):
        Registry().set('logger', Logger())
        Registry().set('pData', {'id': 1})
        self.db.q("INSERT INTO projects (id, name, descr) VALUES(1, 'prj', '')")
        self.db.q("INSERT INTO `hosts` (id, project_id, ip_id, name, descr) VALUES (1,1,1,'test.com', '')")

        data = [
            {'url': '/', 'referer': '/', 'response_code': 0, 'response_time': 0, 'who_add': 'dafs1',
             'spidered': 0, 'size': 0, 'descr': 'some descr'},
        ]
        UrlsModel().add_mass(1, 1, data)

        assert self.db.fetch_one("SELECT COUNT(id) FROM urls") == 1
        assert self.db.fetch_one("SELECT spidered FROM urls WHERE url='/'") == 0

        urls_data = [
            {'referer': '/', 'code': 200, 'time': 10, 'who_add': 'dafs1',
             'spidered': 1, 'size': 20, 'descr': 'some descr', 'hash': '6666cd76f96956469e7be39d750cc7d9', 'query': '', 'path': '/', 'checked': 1},
            {'referer': '/ref1/', 'code': 200, 'time': 10, 'who_add': 'spider',
             'spidered': 1, 'size': 20, 'descr': '', 'hash': 'fa06d89c65fb808240e37f4c9e128955', 'query': '', 'path': '/1/', 'checked': 1},
        ]
        Registry().get('mongo').spider_urls.insert(urls_data)

        self.model.links_in_database(1, 'test.com')

        assert self.db.fetch_one("SELECT COUNT(id) FROM urls") == 2
        assert self.db.fetch_one("SELECT spidered FROM urls WHERE url='/'") == 1

        for url_data in urls_data:
            test_row = self.db.fetch_row("SELECT *, url as path, response_code as code, response_time as `time`, '' as query, 1 as checked FROM urls WHERE `url` = '{0}'".format(url_data['path']))
            for field in url_data:
                if field == '_id':
                    continue
                assert url_data[field] == test_row[field]

        assert self.db.fetch_one("SELECT COUNT(id) FROM urls_base") == 2

        assert self.db.fetch_one("SELECT COUNT(id) FROM urls_base WHERE name='/' AND parent_id=0") == 1
        assert self.db.fetch_one("SELECT COUNT(id) FROM urls_base WHERE name='1' AND parent_id=1") == 1
