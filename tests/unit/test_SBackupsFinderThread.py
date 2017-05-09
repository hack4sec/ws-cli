# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Unit tests for SBackupsFinderThread
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

from classes.threads.SBackupsFinderThread import SBackupsFinderThread
from classes.jobs.BackupsFinderJob import BackupsFinderJob
from classes.FileGenerator import FileGenerator
from classes.Registry import Registry
from classes.Http import Http
from LoggerMock import LoggerMock
from CounterMock import CounterMock
from Common import Common

class Test_SBackupsFinderThread(Common):
    """Unit tests for SBackupsFinderThread"""
    ua = 'Test BF Ua'
    def setup(self):
        requests.get("http://wrtest.com/?clean_log=1")
        requests.get("http://wrtest.com/?protect_disable=1")
        requests.get("http://wrtest.com/?found_disable=1")
        Registry().set('http', Http())
        Registry().set('ua', self.ua)
        Registry().set('logger', LoggerMock())

    run_data = [
        ('get', 'http'),
        ('get', 'https'),
    ]
    @pytest.mark.parametrize("method,protocol", run_data)
    def test_run(self, method, protocol):
        self._test_run(method, protocol)

    def _test_run(self, method, protocol):
        fh = open('/tmp/bf-urls.txt', 'w')
        list_for_find = \
            ['/dir2.zip', '/dir2_old', '/exists.php.b', '/atom.php.back', '/notfound.some', '/notfoundsome.2php']
        for obj in list_for_find:
            fh.write("{0}\n".format(obj))
        fh.close()

        queue = BackupsFinderJob()
        generator = FileGenerator('/tmp/bf-urls.txt')
        queue.set_generator(generator)

        result = []
        thrd = SBackupsFinderThread(
            queue=queue,
            domain='wrtest.com',
            protocol=protocol,
            method=method,
            not_found_re='<h1>Not Found</h1>',
            delay=0,
            ddos_phrase='',
            ddos_human='',
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

        assert result == ['/dir2.zip', '/dir2_old', '/exists.php.b', '/atom.php.back']

        reqs_from_log = requests.get("http://wrtest.com/?get_log=1").text.strip().split("\n")
        assert len(reqs_from_log) == len(list_for_find)
        for req_from_log in reqs_from_log:
            _proto, _ua, _method, _url = req_from_log.split("\t")
            assert _proto.lower() == protocol.lower()
            assert _method.lower() == method.lower()
            assert _url in list_for_find
