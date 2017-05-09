# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Unit tests for DafsThread
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

from classes.threads.DafsThread import DafsThread
from classes.jobs.DafsJob import DafsJob
from classes.FileGenerator import FileGenerator
from classes.Registry import Registry
from classes.Http import Http
from LoggerMock import LoggerMock
from CounterMock import CounterMock
from Common import Common


class Test_DafsThread(Common):
    """Unit tests for DafsThread"""
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
        self.db.q("INSERT INTO projects (id, name, descr) VALUES(1, 'test', '')")
        self.db.q("INSERT INTO ips (id, project_id, ip, descr) VALUES(1, 1, '127.0.0.1', '')")
        self.db.q("INSERT INTO `hosts` (id, project_id, ip_id, name, descr) VALUES (1,1,1,'wrtest.com', 'hd1')")


    run_data = [
        ('get', 'http', 'dirs'),
        ('head', 'http', 'dirs'),
        ('post', 'http', 'dirs'),
        ('get', 'https', 'dirs'),
        ('head', 'https', 'dirs'),
        ('post', 'https', 'dirs'),
        ('get', 'http', 'files'),
        ('head', 'http', 'files'),
        ('post', 'http', 'files'),
        ('get', 'https', 'files'),
        ('head', 'https', 'files'),
        ('post', 'https', 'files')
    ]
    @pytest.mark.parametrize("method,protocol,objs_type", run_data)
    def test_run(self, method, protocol, objs_type):
        self._test_run(method, protocol, objs_type)

    def _make_test_set(self, set_type):
        test_set = []
        if set_type == 'dirs':
            fh = open(testpath + "/files/dafs-dirs.txt")
            for line in fh:
                test_set.append("/{0}/".format(line.strip()))
            fh.close()
        if set_type == 'files':
            fh = open(testpath + "/files/dafs-files.txt")
            for line in fh:
                test_set.append("/{0}".format(line.strip()))
            fh.close()
        return test_set

    def _get_results_set(self, results_type):
        if results_type == 'dirs':
            return [
                {'code': 200, 'time': 0, 'url': '/dir1/'},
                {'code': 403, 'time': 0, 'url': '/dir2/'}
            ]
        else:
            return [
                {'code': 200, 'time': 0, 'url': '/images.php'},
                {'code': 200, 'time': 0, 'url': '/atom.php'},
                {'code': 200, 'time': 0, 'url': '/index.php'},
                {'code': 200, 'time': 0, 'url': '/aaa.php'},
                {'code': 302, 'time': 0, 'url': '/redirect.php'}
            ]

    def _test_run(self, method, protocol, objs_type):
        queue = DafsJob()

        generator = FileGenerator(testpath + "/files/dafs-{0}.txt".format(objs_type), 0)
        queue.set_generator(generator)

        result = []
        thrd = DafsThread(
            queue=queue,
            host='wrtest.com',
            template=('/@/' if objs_type == 'dirs' else '/@'),
            protocol=protocol,
            method=method,
            not_found_re='',
            not_found_size=-1,
            not_found_codes='',
            delay=0,
            counter=CounterMock(),
            result=result,
            mask_symbol='@',
            retest_codes=[],
            ignore_words_re=''
        )
        thrd.setDaemon(True)
        thrd.start()

        start_time = int(time.time())
        while not thrd.done:
            if int(time.time()) - start_time > self.threads_max_work_time:
                pytest.fail("Thread work {0} secs".format(int(time.time()) - start_time))
            time.sleep(1)

        for row in result:
            result[result.index(row)]['time'] = 0

        assert result == self._get_results_set(objs_type)

        test_set = self._make_test_set(objs_type)
        reqs_from_log = requests.get("http://wrtest.com/?get_log=1").text.strip().split("\n")
        assert len(reqs_from_log) == len(test_set)
        for req_from_log in reqs_from_log:
            _proto, _ua, _method, _url = req_from_log.split("\t")
            assert _proto.lower() == protocol.lower()
            assert _ua == self.ua
            assert _method.lower() == method.lower()
            assert _url in test_set
