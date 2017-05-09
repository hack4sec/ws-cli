# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Unit tests for ParamsBruterThread
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

from classes.threads.ParamsBruterThread import ParamsBruterThread
from classes.jobs.ParamsBruterJob import ParamsBruterJob
from classes.FileGenerator import FileGenerator
from classes.Registry import Registry
from classes.Http import Http
from LoggerMock import LoggerMock
from CounterMock import CounterMock
from Common import Common


class Test_ParamsBruterThread(Common):
    """Unit tests for ParamsBruterThread"""
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
        ('post', 'http'),
        ('get', 'https'),
        ('post', 'https'),
    ]
    @pytest.mark.parametrize("method,protocol", run_data)
    def test_run(self, method, protocol):
        self._test_run(method, protocol)

    def _test_run(self, method, protocol):
        fh = open('/tmp/params.txt', 'w')
        list_for_find = ['abc', 'param', 'def']
        for obj in list_for_find:
            fh.write("{0}\n".format(obj))
        fh.close()

        queue = ParamsBruterJob()
        generator = FileGenerator('/tmp/params.txt')
        queue.set_generator(generator)

        result = []
        thrd = ParamsBruterThread(
            queue=queue,
            protocol=protocol,
            host='wrtest.com',
            url='/params-{0}.php?'.format(method),
            max_params_length=100,
            value='a',
            method=method,
            mask_symbol='@',
            not_found_re='',
            not_found_size=0,
            not_found_codes='',
            retest_codes='',
            delay=0,
            ignore_words_re='',
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

        assert result == ['param=a']
