# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Unit tests for SFormBruterThread
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

from classes.threads.SFormBruterThread import SFormBruterThread
from classes.jobs.FormBruterJob import FormBruterJob
from classes.FileGenerator import FileGenerator
from classes.Registry import Registry
from classes.Http import Http
from LoggerMock import LoggerMock
from CounterMock import CounterMock
from Common import Common


class Test_SFormBruterThread(Common):
    """Unit tests for SFormBruterThread"""
    def setup(self):
        Registry().set('http', Http())
        Registry().set('ua', '')
        Registry().set('logger', LoggerMock())
        self.db.q("TRUNCATE TABLE projects")
        self.db.q("TRUNCATE TABLE ips")
        self.db.q("TRUNCATE TABLE hosts")
        self.db.q("INSERT INTO projects (id, name, descr) VALUES(1, 'test', '')")
        self.db.q("INSERT INTO ips (id, project_id, ip, descr) VALUES(1, 1, '127.0.0.1', '')")
        self.db.q("INSERT INTO `hosts` (id, project_id, ip_id, name, descr) VALUES (1,1,1,'wrtest.com', 'hd1')")

    brute_data = [
        ('http'),
        ('https')
    ]
    @pytest.mark.parametrize("protocol", brute_data)
    def test_brute(self, protocol):
        self._test_brute(protocol)

    def _test_brute(self, protocol):
        queue = FormBruterJob()
        generator = FileGenerator(testpath + "/files/pass.txt", 0, 0)
        queue.set_generator(generator)

        result = []

        thrd = SFormBruterThread(
            queue=queue,
            protocol=protocol,
            host='wrtest.com',
            url='/auth.php',
            false_phrase='',
            true_phrase='Success!',
            delay=0,
            first_stop=True,
            login='root',
            conffile=testpath + '/files/form-bruter-false.cfg',
            pass_min_len=0,
            pass_max_len=0,
            counter=CounterMock(),
            result=result,
            pass_found=False,
            ddos_human='',
            ddos_phrase='',
            recreate_phrase=''
        )
        thrd.setDaemon(True)
        thrd.start()

        start_time = int(time.time())
        while not thrd.done:
            if int(time.time()) - start_time > self.threads_max_work_time:
                pytest.fail("Thread work {0} secs".format(int(time.time()) - start_time))
            time.sleep(1)

        assert result == \
               [{'content': '<html xmlns="http://www.w3.org/1999/xhtml"><head></head><body>Success!</body></html>',
                 'word': 'qwerty'}]
