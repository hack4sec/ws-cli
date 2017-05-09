# -*- coding: utf-8 -*-

import shutil
import re
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

from classes.threads.SSpiderThread import SSpiderThread
from classes.jobs.SpiderJob import SpiderJob
from classes.SpiderCommon import SpiderCommon
from classes.SpiderRequestsCounter import SpiderRequestsCounter
from classes.FileGenerator import FileGenerator
from classes.Registry import Registry
from classes.Http import Http
from LoggerMock import LoggerMock
from CounterMock import CounterMock
from Common import Common
from libs.common import mongo_result_to_list


class Test_CmsThread(Common):
    ua = 'Test BF Ua'
    def setup(self):
        requests.get("http://wrtest.com/?clean_log=1")
        requests.get("http://wrtest.com/?protect_disable=1")
        requests.get("http://wrtest.com/?found_disable=1")
        Registry().set('http', Http())
        Registry().set('ua', self.ua)
        Registry().set('logger', LoggerMock())
        Registry().set('pData', {'id': 1})
        Registry().set('data_path', '/tmp/')
        Registry().set('denied_schemes', ['mailto', 'javascript'])
        Registry().set('allow_regexp', re.compile(''))
        if os.path.exists("/tmp/wrtest.com"):
            shutil.rmtree("/tmp/wrtest.com")
        os.mkdir("/tmp/wrtest.com")

        self.db.q("TRUNCATE TABLE `projects`")
        self.db.q("TRUNCATE TABLE `ips`")
        self.db.q("TRUNCATE TABLE `hosts`")
        self.db.q("TRUNCATE TABLE `hosts_info`")
        self.db.q("TRUNCATE TABLE `urls`")
        self.db.q("TRUNCATE TABLE `requests`")
        self.db.q("INSERT INTO projects (id, name, descr) VALUES(1, 'test', '')")
        self.db.q("INSERT INTO ips (id, project_id, ip, descr) VALUES(1, 1, '127.0.0.1', '')")
        self.db.q("INSERT INTO `hosts` (id, project_id, ip_id, name, descr) VALUES (1,1,1,'wrtest.com', 'hd1')")

    def test_run(self):
        SpiderCommon.prepare_first_pages('wrtest.com')

        thrd = SSpiderThread(
            job=SpiderJob(),
            host='wrtest.com',
            protocol='http',
            src=SpiderRequestsCounter(100),
            delay=0,
            not_found_re='<h1>Not Found</h1>',
            ddos_human='',
            ddos_phrase='',
            recreate_re='',
            counter=CounterMock()
        )
        thrd.setDaemon(True)
        thrd.start()

        start_time = int(time.time())
        while thrd.running:
            if int(time.time()) - start_time > self.threads_max_work_time:
                pytest.fail("Thread work {0} secs".format(int(time.time()) - start_time))
            time.sleep(1)

        counts = {
            '/exists.php': 16,
            #'/images.php': 6,
            '/page.php': 1,
            '/': 1,
            '/not-exists.php': 1,
            '/not-exists.svg': 1,
            '/style.css': 1,
            '/style-compressed.css': 1,
            #'/redirect-target.php': 1,
            '/redirect.php': 1,
            '/code.js': 1,
            '/compressed.js': 1,
            '/slow.php': 1,
            '/rss.php': 1,
            '/custom-xml.php': 1,
            '/dir1': 1,
            '/dir2': 1,
            '/syntax-error-xml.php': 1,
            '/exist': 1,
            '/exist2': 1,
            '/maxsize': 1,
            '/deep/': 1,
            '/deep/moredeep/': 1,
            '/deep/moredeep/dir1/': 1
        }
        for path in counts:
            print path
            assert Registry().get('mongo').spider_urls.find({'path': path}).count() == counts[path]
