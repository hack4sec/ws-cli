# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Unit tests for FuzzerHeadersThread
"""

import sys
import os
import time
import pytest

wrpath = os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + '/../../')
testpath = os.path.realpath(os.path.dirname(os.path.realpath(__file__)))

sys.path.append(wrpath)
sys.path.append(wrpath + '/classes')
sys.path.append(wrpath + '/classes/models')
sys.path.append(wrpath + '/classes/kernel')
sys.path.append(testpath + '/classes')

from classes.threads.FuzzerHeadersThread import FuzzerHeadersThread
from classes.jobs.FuzzerHeadersJob import FuzzerHeadersJob
from classes.Registry import Registry
from classes.Http import Http
from LoggerMock import LoggerMock
from CounterMock import CounterMock
from Common import Common


class Test_FuzzerHeadersThread(Common):
    """Unit tests for FuzzerHeadersThread"""
    def setup(self):
        Registry().set('http', Http())
        Registry().set('ua', '')
        Registry().set('logger', LoggerMock())
        Registry().set(
            'fuzzer_evil_value',
            open(wrpath + "/bases/fuzzer-evil-value.txt").read().strip()
        )
        self.db.q("TRUNCATE TABLE projects")
        self.db.q("TRUNCATE TABLE ips")
        self.db.q("TRUNCATE TABLE hosts")
        self.db.q("INSERT INTO projects (id, name, descr) VALUES(1, 'test', '')")
        self.db.q("INSERT INTO ips (id, project_id, ip, descr) VALUES(1, 1, '127.0.0.1', '')")
        self.db.q("INSERT INTO `hosts` (id, project_id, ip_id, name, descr) VALUES (1,1,1,'wrtest.com', 'hd1')")

    run_data = [
        ('get', 'http'),
        ('head', 'http'),
        ('post', 'http'),
        ('get', 'https'),
        ('head', 'https'),
        ('post', 'https'),
    ]
    @pytest.mark.parametrize("method,protocol", run_data)
    def test_brute(self, method, protocol):
        self._test_brute(method, protocol)

    def _test_brute(self, method, protocol):
        queue = FuzzerHeadersJob()
        queue.load_dict(['/fuzz-h.php?a=1&b=2', '/fuzz-500.php?c=1', '/maxsize'])

        result = []

        thrd = FuzzerHeadersThread(
            queue=queue,
            domain='wrtest.com',
            protocol=protocol,
            method=method,
            delay=0,
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
            {'header': 'X-Client-Ip', 'url': u'/fuzz-h.php?a=1&b=2', 'words': ['500 Status code']},
            {'header': 'X-Forwarded-For', 'url': u'/fuzz-500.php?c=1', 'words': ['500 Status code']}
        ]
