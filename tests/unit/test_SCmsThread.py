# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Unit tests for SCmsThread
"""

import sys
import os
import time
import pytest
import requests

wrpath = os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + '/../../')
testpath = os.path.realpath(os.path.dirname(os.path.realpath(__file__)))

sys.path.append(wrpath)
sys.path.append(wrpath + '/classes')
sys.path.append(wrpath + '/classes/models')
sys.path.append(wrpath + '/classes/kernel')
sys.path.append(testpath + '/classes')

from classes.threads.SCmsThread import SCmsThread
from classes.jobs.CmsJob import CmsJob
from classes.Registry import Registry
from classes.Http import Http
from classes.models.CmsModel import CmsModel
from LoggerMock import LoggerMock
from CounterMock import CounterMock
from Common import Common


class Test_SCmsThread(Common):
    """Unit tests for SCmsThread"""
    ua = 'Test BF Ua'
    def setup(self):
        requests.get("http://wrtest.com/?clean_log=1")
        requests.get("http://wrtest.com/?protect_disable=1")
        requests.get("http://wrtest.com/?found_disable=1")
        Registry().set('http', Http())
        Registry().set('ua', self.ua)
        Registry().set('logger', LoggerMock())

        self.db.q("TRUNCATE TABLE `projects`")
        self.db.q("TRUNCATE TABLE `ips`")
        self.db.q("TRUNCATE TABLE `hosts`")
        self.db.q("TRUNCATE TABLE `hosts_info`")
        self.db.q("TRUNCATE TABLE `urls`")
        self.db.q("TRUNCATE TABLE `requests`")
        self.db.q("TRUNCATE TABLE `cms`")
        self.db.q("TRUNCATE TABLE `cms_paths`")
        self.db.q("TRUNCATE TABLE `cms_paths_hashes`")

        self.db.q("INSERT INTO projects (id, name, descr) VALUES(1, 'test', '')")
        self.db.q("INSERT INTO ips (id, project_id, ip, descr) VALUES(1, 1, '127.0.0.1', '')")
        self.db.q("INSERT INTO `hosts` (id, project_id, ip_id, name, descr) VALUES (1,1,1,'wrtest.com', 'hd1')")

        self.db.q("INSERT INTO `cms` (`id`, `name`) VALUES "
                  "(1, 'SomeCms1'),"
                  "(2, 'SomeCms2');")
        self.db.q("INSERT INTO `cms_paths` (`id`, `hash_id`, `cms_id`) "
                  "VALUES (1, 1, 1),(2, 2, 1),(3, 3, 1),(4, 4, 1),"
                  "(5, 5, 1),(6, 6, 2),(7, 7, 2),(8, 8, 2),(9, 9, 2)")
        self.db.q("INSERT INTO `cms_paths_hashes` (`id`, `hash`, `path`) VALUES "
                  "(1, '61ceaea1fd6f4643709a1a445285c425', '/dle/'),"
                  "(2, '81fc224d016d5c80a6ae3b0e792d3ce1', '/files/'),"
                  "(3, 'a53a3d606f3e156ffd8675415879f057', '/images/'),"
                  "(4, 'f3cd3ed7adf1c65207c97e8f652b3f28', '/jui/'),"
                  "(5, 'e7d2b5f52bf8c09d264746caf03fdd4b', '/maxsize'),"
                  "(6, 'a2c180452d0aaaff54812a20c88c23fa', '/a/'),"
                  "(7, '3c66d6e91e24880f0e8cbac25e2dcd30', '/b/'),"
                  "(8, '8eb5114ef2ecd911d64c8a138f5cc5f5', '/c/'),"
                  "(9, 'bdbf61f7218a2d3a09b21e7c3b0cda8f', '/d/')")

    run_data = [
        ('get', 'http'),
        ('get', 'https'),
    ]
    @pytest.mark.parametrize("method,protocol", run_data)
    def test_run(self, method, protocol):
        self._test_run(method, protocol)

    def _test_run(self, method, protocol):
        model = CmsModel()

        queue = CmsJob()
        for item in model.all_paths_list():
            queue.put(item.strip())

        result = []
        thrd = SCmsThread(
            queue=queue,
            domain='wrtest.com',
            url='/',
            protocol=protocol,
            method=method,
            not_found_re='<h1>Not Found</h1>',
            delay=0,
            ddos_human='',
            ddos_phrase='',
            recreate_re='',
            counter=CounterMock(),
            result=result
        )
        thrd.setDaemon(True)
        thrd.start()

        start_time = int(time.time())
        while not thrd.done:
            if int(time.time()) - start_time > self.threads_max_work_time:
                pytest.fail("Thread work {0} secs".format(int(time.time()) - start_time))
            time.sleep(1)

        assert result == [
            {'code': 0, 'path': u'/files/'},
            {'code': 0, 'path': u'/maxsize'},
            {'code': 0, 'path': u'/a/'},
            {'code': 0, 'path': u'/b/'},
            {'code': 0, 'path': u'/c/'}
        ]

        urls_to_skip = [
            '/redirect-target.php', '/code.js', '/compressed.js', '/style.css', '/style-compressed.css'
        ]
        test_urls_set = ['/dle/', '/files/', '/images/', '/jui/', '/maxsize', '/a/', '/b/', '/c/', '/d/', '/']
        reqs_from_log = requests.get("http://wrtest.com/?get_log=1").text.strip().split("\n")
        assert len(reqs_from_log)-5 == self.db.fetch_one("SELECT COUNT(id) FROM cms_paths_hashes")
        for req_from_log in reqs_from_log:
            _proto, _ua, _method, _url = req_from_log.split("\t")
            assert _proto.lower() == protocol.lower()
            assert _method.lower() == method.lower()
            if _url not in urls_to_skip:
                assert _url in test_urls_set
