# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Unit tests for UrlsModel
"""

import sys
import os
import pytest

wrpath = os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + '/../../')
testpath = os.path.realpath(os.path.dirname(os.path.realpath(__file__)))

sys.path.append(wrpath)
sys.path.append(wrpath + '/classes')
sys.path.append(testpath + '/classes')
sys.path.append(wrpath + '/classes/models')
sys.path.append(wrpath + '/classes/jobs')
sys.path.append(wrpath + '/classes/threads')
sys.path.append(wrpath + '/classes/kernel')

from Common import Common
from classes.models.UrlsModel import UrlsModel
from classes.kernel.WSException import WSException
from libs.common import md5

class Test_UrlsModel(Common):
    """Unit tests for UrlsModel"""
    model = None

    def setup(self):
        self.model = UrlsModel()
        self.db.q("TRUNCATE TABLE urls")
        self.db.q("TRUNCATE TABLE urls_base")
        self.db.q("TRUNCATE TABLE urls_base_params")
        self.db.q("TRUNCATE TABLE projects")
        self.db.q("TRUNCATE TABLE hosts")
        self.db.q("TRUNCATE TABLE ips")

    def test_one_add(self):
        assert self.db.fetch_one("SELECT 1 FROM urls") is None

        _id = self.model.add(1, 2, '/1/', '/ref', 200, 10, 'dafs', 1, 100, 'desc')
        assert bool(_id)

        test_url = self.db.fetch_row("SELECT * FROM urls WHERE id = " + str(_id))

        assert test_url['project_id'] == 1
        assert test_url['host_id'] == 2
        assert test_url['hash'] == md5('/1/')
        assert test_url['url'] == '/1/'
        assert test_url['referer'] == '/ref'
        assert test_url['response_code'] == 200
        assert test_url['response_time'] == 10
        assert test_url['size'] == 100
        assert test_url['descr'] == 'desc'
        assert test_url['spidered'] == 1

    def test_add_mass(self):
        assert self.db.fetch_one("SELECT 1 FROM urls") is None

        data = [
            {'url': '/1/', 'referer': '/ref1/', 'response_code': 401, 'response_time': 10,
             'who_add': 'dafs', 'spidered': 1, 'size': 20, 'descr': 'some descr'},
            {'url': '/2/', 'response_code': 401, 'response_time': 10, 'who_add': 'dafs',
             'spidered': 1, 'size': 20, 'descr': 'some descr'},
            {'url': '/3/', 'referer': '/ref3/', 'response_time': 10, 'who_add': 'dafs',
             'spidered': 1, 'size': 20, 'descr': 'some descr'},
            {'url': '/4/', 'referer': '/ref4/', 'response_code': 401, 'who_add': 'dafs',
             'spidered': 1, 'size': 20, 'descr': 'some descr'},
            {'url': '/5/', 'referer': '/ref5/', 'response_code': 401, 'response_time': 10,
             'spidered': 1, 'size': 20, 'descr': 'some descr'},
            {'url': '/6/', 'referer': '/ref6/', 'response_code': 401, 'response_time': 10,
             'who_add': 'dafs', 'size': 20, 'descr': 'some descr'},
            {'url': '/7/', 'referer': '/ref7/', 'response_code': 401, 'response_time': 10,
             'who_add': 'dafs', 'spidered': 1, 'descr': 'some descr'},
            {'url': '/8/', 'referer': '/ref8/', 'response_code': 401, 'response_time': 10,
             'who_add': 'dafs', 'spidered': 1, 'size': 20}
        ]
        test_data = [
            {'url': '/1/', 'referer': '/ref1/', 'response_code': 401, 'response_time': 10, 'who_add': 'dafs',
             'spidered': 1, 'size': 20, 'descr': 'some descr'},
            {'url': '/2/', 'referer': '', 'response_code': 401, 'response_time': 10, 'who_add': 'dafs',
             'spidered': 1, 'size': 20, 'descr': 'some descr'},
            {'url': '/3/', 'referer': '/ref3/', 'response_code': 0, 'response_time': 10, 'who_add': 'dafs',
             'spidered': 1, 'size': 20, 'descr': 'some descr'},
            {'url': '/4/', 'referer': '/ref4/', 'response_code': 401, 'response_time': 0, 'who_add': 'dafs',
             'spidered': 1, 'size': 20, 'descr': 'some descr'},
            {'url': '/5/', 'referer': '/ref5/', 'response_code': 401, 'response_time': 10, 'who_add': 'human',
             'spidered': 1, 'size': 20, 'descr': 'some descr'},
            {'url': '/6/', 'referer': '/ref6/', 'response_code': 401, 'response_time': 10, 'who_add': 'dafs',
             'spidered': 0, 'size': 20, 'descr': 'some descr'},
            {'url': '/7/', 'referer': '/ref7/', 'response_code': 401, 'response_time': 10, 'who_add': 'dafs',
             'spidered': 1, 'size': 0, 'descr': 'some descr'},
            {'url': '/8/', 'referer': '/ref8/', 'response_code': 401, 'response_time': 10, 'who_add': 'dafs',
             'spidered': 1, 'size': 20, 'descr': ''},
        ]
        self.model.add_mass(1, 2, data)
        for test_url in self.db.fetch_all("SELECT * FROM urls ORDER BY id ASC"):
            test_key = test_url['id']-1
            assert test_url['project_id'] == 1
            assert test_url['host_id'] == 2
            assert test_url['hash'] == md5(test_data[test_key]['url'])
            assert test_url['url'] == test_data[test_key]['url']
            assert test_url['referer'] == \
                   ('' if 'referer' not in test_data[test_key].keys() else test_data[test_key]['referer'])
            assert test_url['response_code'] == \
                   (0 if 'response_code' not in test_data[test_key].keys() else test_data[test_key]['response_code'])
            assert test_url['response_time'] == \
                   (0 if 'response_time' not in test_data[test_key].keys() else test_data[test_key]['response_time'])
            assert test_url['size'] == (0 if 'size' not in test_data[test_key].keys() else test_data[test_key]['size'])
            assert test_url['who_add'] == \
                   ('human' if 'who_add' not in test_data[test_key].keys() else test_data[test_key]['who_add'])
            assert test_url['descr'] == \
                   ('' if 'descr' not in test_data[test_key].keys() else test_data[test_key]['descr'])
            assert test_url['spidered'] == \
                   (0 if 'spidered' not in test_data[test_key].keys() else test_data[test_key]['spidered'])

    def test_add_mass_wo_url(self):
        with pytest.raises(WSException) as ex:
            self.model.add_mass(1, 2, [{'aaa': 'bbb'}])
        assert "ERROR: URL row must have a 'url' key" in str(ex)

    def test_add_mass_left_field(self):
        with pytest.raises(WSException) as ex:
            self.model.add_mass(1, 2, [{'url': 'aaa', 'aaa': 'bbb'}])
        assert "ERROR: Key 'aaa' must not be in url data" in str(ex)

    def test_list_by_host_name(self):
        self.db.q("INSERT INTO `hosts` (`id`, `project_id`, `ip_id`, `name`, `descr`) VALUES(2, 1, 1, 'test.com', '')")

        data = [
            {'url': '/1/', 'referer': '/ref1/', 'response_code': 401, 'response_time': 10,
             'who_add': 'dafs1', 'spidered': 1, 'size': 20, 'descr': 'some descr'},
            {'url': '/2/', 'referer': '/ref2/', 'response_code': 402, 'response_time': 10,
             'who_add': 'dafs2', 'spidered': 1, 'size': 20, 'descr': 'some descr'},
            {'url': '/3/', 'referer': '/ref3/', 'response_code': 403, 'response_time': 10,
             'who_add': 'dafs3', 'spidered': 1, 'size': 20, 'descr': 'some descr'},
            {'url': '/4/', 'referer': '/ref4/', 'response_code': 200, 'response_time': 10,
             'who_add': 'dafs4', 'spidered': 1, 'size': 20, 'descr': 'some descr'},
            {'url': '/5/', 'referer': '/ref5/', 'response_code': 201, 'response_time': 10,
             'who_add': 'dafs5', 'spidered': 1, 'size': 20, 'descr': 'some descr'},
            {'url': '/6/', 'referer': '/ref6/', 'response_code': 301, 'response_time': 10,
             'who_add': 'dafs6', 'spidered': 1, 'size': 20, 'descr': 'some descr'},
            {'url': '/7/', 'referer': '/ref7/', 'response_code': 501, 'response_time': 10,
             'who_add': 'dafs7', 'spidered': 1, 'size': 20, 'descr': 'some descr'},
            {'url': '/8/', 'referer': '/ref8/', 'response_code': 101, 'response_time': 10,
             'who_add': 'dafs8', 'spidered': 1, 'size': 20, 'descr': 'some descr'},
        ]
        self.model.add_mass(1, 2, data)

        urls = self.model.list_by_host_name(1, 'test.com')
        assert len(urls) == len(data)

        k = 0
        for url in urls:
            assert url['url'] == data[k]['url']
            assert url['code'] == data[k]['response_code']
            assert url['time'] == data[k]['response_time']
            assert url['who_add'] == data[k]['who_add']
            assert url['descr'] == data[k]['descr']
            k += 1

    def test_list_by_host_name_for_spider(self):
        self.db.q("INSERT INTO `hosts` (`id`, `project_id`, `ip_id`, `name`, `descr`) VALUES(2, 1, 1, 'test.com', '')")

        data = [
            {'url': '/1/', 'referer': '/ref1/', 'response_code': 401, 'response_time': 10,
             'who_add': 'dafs1', 'spidered': 0, 'size': 20, 'descr': 'some descr'},
            {'url': '/2/', 'referer': '/ref2/', 'response_code': 402, 'response_time': 10,
             'who_add': 'dafs2', 'spidered': 0, 'size': 20, 'descr': 'some descr'},
            {'url': '/3/', 'referer': '/ref3/', 'response_code': 403, 'response_time': 10,
             'who_add': 'dafs3', 'spidered': 1, 'size': 20, 'descr': 'some descr'},
            {'url': '/4/', 'referer': '/ref4/', 'response_code': 200, 'response_time': 10,
             'who_add': 'dafs4', 'spidered': 1, 'size': 20, 'descr': 'some descr'},
            {'url': '/5/', 'referer': '/ref5/', 'response_code': 201, 'response_time': 10,
             'who_add': 'dafs5', 'spidered': 1, 'size': 20, 'descr': 'some descr'},
            {'url': '/6/', 'referer': '/ref6/', 'response_code': 301, 'response_time': 10,
             'who_add': 'dafs6', 'spidered': 1, 'size': 20, 'descr': 'some descr'},
            {'url': '/7/', 'referer': '/ref7/', 'response_code': 501, 'response_time': 10,
             'who_add': 'dafs7', 'spidered': 1, 'size': 20, 'descr': 'some descr'},
            {'url': '/8/', 'referer': '/ref8/', 'response_code': 101, 'response_time': 10,
             'who_add': 'dafs8', 'spidered': 1, 'size': 20, 'descr': 'some descr'},
        ]
        self.model.add_mass(1, 2, data)
        data = [data[0], data[1]]

        urls = self.model.list_by_host_name_for_spider(1, 'test.com')
        assert len(urls) == len(data)

        k = 0
        for url in urls:
            assert url['url'] == data[k]['url']
            assert url['code'] == data[k]['response_code']
            assert url['time'] == data[k]['response_time']
            assert url['who_add'] == data[k]['who_add']
            assert url['descr'] == data[k]['descr']
            k += 1

    def test_exists(self):
        self.db.q("INSERT INTO `hosts` (`id`, `project_id`, `ip_id`, `name`, `descr`) VALUES(2, 1, 1, 'test.com', '')")
        self.model.add(1, 2, '/1/', '/ref', 200, 10, 'dafs', 1, 100, 'desc')
        assert self.model.exists(1, 'test.com', '/1/')
        assert  not self.model.exists(1, 'test.com', '/2/')

    def test_delete(self):
        self.db.q("INSERT INTO `hosts` (`id`, `project_id`, `ip_id`, `name`, `descr`) VALUES(2, 1, 1, 'test.com', '')")
        self.model.add(1, 2, '/1/', '/ref', 200, 10, 'dafs', 1, 100, 'desc')
        assert self.model.exists(1, 'test.com', '/1/')
        self.model.delete(1, 'test.com', '/1/')
        assert not self.model.exists(1, 'test.com', '/1/')

    def test_update_url_field(self):
        self.db.q("INSERT INTO `hosts` (`id`, `project_id`, `ip_id`, `name`, `descr`) VALUES(2, 1, 1, 'test.com', '')")
        self.model.add(1, 2, '/1/', '/ref', 200, 10, 'dafs', 1, 100, 'desc')
        assert self.db.fetch_one("SELECT response_code FROM urls") == 200
        self.model.update_url_field(1, 'test.com', '/1/', 'response_code', 300)
        assert self.db.fetch_one("SELECT response_code FROM urls") == 300

    def test_update_url_field_mass(self):
        self.db.q("INSERT INTO `hosts` (`id`, `project_id`, `ip_id`, `name`, `descr`) VALUES(2, 1, 1, 'test.com', '')")

        self.model.add(1, 2, '/1/', '/ref', 200, 10, 'dafs', 1, 100, 'desc')
        self.model.add(1, 2, '/2/', '/ref', 200, 10, 'dafs', 1, 100, 'desc')

        update_data = [{'url': '/1/', 'value': 300}, {'url': '/2/', 'value': 400}]
        self.model.update_url_field_mass(1, 'test.com', 'response_code', update_data)

        assert self.db.fetch_one("SELECT response_code FROM urls WHERE url='/1/'") == 300
        assert self.db.fetch_one("SELECT response_code FROM urls WHERE url='/2/'") == 400
