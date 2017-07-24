# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Unit tests for DnsBruteThread
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

from classes.threads.DnsBruteThread import DnsBruteThread
from classes.jobs.DnsBruteJob import DnsBruteJob
from classes.FileGenerator import FileGenerator
from classes.Registry import Registry
from LoggerMock import LoggerMock
from CounterMock import CounterMock
from Common import Common


class Test_DnsBruteThread(Common):
    """Unit tests for DnsBruteThread"""
    def setup(self):
        Registry().set('logger', LoggerMock())

    brute_data = [
        ('tcp'),
        ('udp')
    ]
    @pytest.mark.parametrize("protocol", brute_data)
    def test_brute(self, protocol):
        self._test_brute(protocol)

    def _test_brute(self, protocol):
        queue = DnsBruteJob()
        generator = FileGenerator(testpath + "/files/dns.txt", 0, 0)
        queue.set_generator(generator)

        result = []

        thrd = DnsBruteThread(
            queue=queue,
            domains='wrtest.com',
            template='@',
            proto=protocol,
            msymbol='@',
            ignore_ip='',
            dns_srv='127.0.0.1',
            delay=0,
            http_nf_re='',
            ignore_words_re='',
            result=result,
            counter=CounterMock()
        )
        thrd.setDaemon(True)
        thrd.start()

        start_time = int(time.time())
        while not thrd.done:
            if int(time.time()) - start_time > self.threads_max_work_time:
                pytest.fail("Thread work {0} secs".format(int(time.time()) - start_time))
            time.sleep(1)

        assert result == [
            {'dns': '127.0.0.1', 'ip': u'127.0.0.1', 'name': 'aaa.wrtest.com'},
            {'dns': '127.0.0.1', 'ip': u'127.0.0.1', 'name': 'www.wrtest.com'}
        ]
