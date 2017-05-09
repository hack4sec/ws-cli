# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Unit tests for FuzzerUrlsThread
"""

import sys
import os
import time
from urlparse import urlparse
import pytest


wrpath = os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + '/../../')
testpath = os.path.realpath(os.path.dirname(os.path.realpath(__file__)))

sys.path.append(wrpath)
sys.path.append(wrpath + '/classes')
sys.path.append(wrpath + '/classes/models')
sys.path.append(wrpath + '/classes/kernel')
sys.path.append(testpath + '/classes')

from classes.threads.FuzzerUrlsThread import FuzzerUrlsThread
from classes.jobs.FuzzerUrlsJob import FuzzerUrlsJob
from classes.Registry import Registry
from classes.Http import Http
from classes.FileGenerator import FileGenerator
from LoggerMock import LoggerMock
from CounterMock import CounterMock
from Common import Common


class Test_FuzzerUrlsThread(Common):
    """Unit tests for FuzzerUrlsThread"""
    def setup(self):
        Registry().set('wr_path', wrpath)
        Registry().set('http', Http())
        Registry().set('ua', '')
        Registry().set('logger', LoggerMock())
        Registry().set(
            'fuzzer_evil_value',
            open(wrpath + "/bases/fuzzer-evil-value.txt").read().strip()
        )

    brute_data = [
        ('http'),
        ('https')
    ]
    @pytest.mark.parametrize("protocol", brute_data)
    def test_brute(self, protocol):
        self._test_brute(protocol)

    def _parse_params(self, query):
        """ Parse url params string to dict """
        result = []
        params = query.split("&")
        for param in params:
            param = param.split("=")
            result.append({"name": param[0], "value": "" if len(param) == 1 else param[1]})
        return result

    def _generate_fuzz_urls(self, url):
        """ Parse urls and make a fuzzer urls from it """
        templates = open(Registry().get('wr_path') + "/bases/fuzzer-templates.txt").readlines()
        result = []
        url = urlparse(url)
        if len(url.query):
            params = self._parse_params(url.query.strip())

            for template in templates:
                template = template.strip()

                for n in range(0, len(params)):
                    path = url.path + '?'
                    for param in params:
                        if params.index(param) == n:
                            path += template.replace("|name|", param['name']).replace("|value|", param['value']) + "&"
                        else:
                            path += "{0}={1}&".format(param['name'], param['value'])
                    result.append(path)
        return result

    def _test_brute(self, protocol):
        fh = open('/tmp/fuzz.txt', 'w')
        for url in ['/fuzz-h.php?a=1&b=2', '/fuzz-500.php?c=1', '/maxsize?a=1']:
            for fuzz_url in self._generate_fuzz_urls(url):
                fh.write(fuzz_url + "\n")
        fh.close()

        queue = FuzzerUrlsJob()
        generator = FileGenerator('/tmp/fuzz.txt', 0, 0)
        queue.set_generator(generator)

        result = []

        thrd = FuzzerUrlsThread(
            queue=queue,
            domain='wrtest.com',
            protocol=protocol,
            method='get',
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
            {'url': '/fuzz-500.php?c[]=1&', 'words': ['500 Status code']},
            {'url': '/fuzz-500.php?c[][]=1&', 'words': ['500 Status code']}
        ]
