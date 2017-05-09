# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Tests of Cms module
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
sys.path.append(testpath + '/classes')
sys.path.append(wrpath + '/classes/models')
sys.path.append(wrpath + '/classes/jobs')
sys.path.append(wrpath + '/classes/threads')
sys.path.append(wrpath + '/classes/kernel')

from CommonTest import CommonTest
from libs.common import file_get_contents, md5sum, t

class Test_RunCms(CommonTest):
    """Tests of Cms module"""
    method = None
    check_method = None
    use_https = False
    selenium = False
    found_items = None

    def setup(self):
        CommonTest.setup(self)

        self.method = None
        self.check_method = None
        self.use_https = False
        self.selenium = False

        requests.get("http://wrtest.com/?clean_log=1")
        requests.get("http://wrtest.com/?protect_disable=1")

    def _prepare_db(self):
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

    def _how_many_variants(self):
        """How many variants for requests we have?"""
        return self.db.fetch_one("SELECT COUNT(id) FROM cms_paths_hashes")

    def _check_logger(self):
        """Check logger work"""
        logs_path = "{0}/logs/cms/{1}/".format(wrpath, t("%Y-%m-%d"))
        time_dir = sorted(os.listdir(logs_path))[-1]

        run_log_data = file_get_contents("{0}/{1}/run.log".format(logs_path, time_dir))
        assert "Loaded {0} variants".format(self._how_many_variants()) in run_log_data
        if not self.selenium:
            for item in self.found_items:
                if self.check_method is not 'head':
                    assert item['sum'] == md5sum("{0}/{1}/items/{2}".format(logs_path, time_dir, item['log']))

    def _check_requests_log(self):
        """Checking requets log from server"""
        resp = requests.get("http://wrtest.com/?get_log=1").text.strip()
        # Selenium make 5 other requests - redirect to roos and css/js from there
        assert len(resp.split("\n")) == self._how_many_variants() \
            if not self.selenium else self._how_many_variants() + 5

        for _str in resp.split("\n"):
            tmp_protocol, tmp_ua, tmp_method, tmp_url = _str.split("\t")
            assert tmp_method.lower() == self.check_method.lower()
            assert tmp_protocol.lower() == ('https' if self.use_https else 'http')

        tmp_list_orig = resp.split("\n")
        sorted(tmp_list_orig)
        tmp_list_uniq = list(set(resp.split("\n")))
        sorted(tmp_list_uniq)

        assert len(tmp_list_orig) == len(tmp_list_uniq)

    def _usual_scan(self, additional_params=None):
        """
        Common method for usual scan
        :param additional_params:
        :return:
        """
        additional_params = additional_params or []
        self._prepare_db()

        self.found_items = [
            {
                'name': u'/a/',
                'sum': 'ff713794b3cce1f8a497075335c45280',
                'log': 'a_.txt'
            },
            {
                'name': u'/b/',
                'sum': 'ff713794b3cce1f8a497075335c45280',
                'log': 'b_.txt'
            },
            {
                'name': u'/c/',
                'sum': 'ff713794b3cce1f8a497075335c45280',
                'log': 'c_.txt'
            },
            {
                'name': u'/files/',
                'sum': 'b1d3458651d61acc90e0d3b233412c4f',
                'log': 'files_.txt'
            },
        ]

        run_params = [
            './main.py', 'test', 'Cms', 'scan', '--host=wrtest.com', '--threads=3',
        ]
        run_params.extend(additional_params)

        if self.method:
            run_params.append('--method=' + self.method)
        if self.use_https:
            run_params.append('--protocol=https')

        out = self._run('normal', run_params)

        assert out.count('SomeCms2') == 1
        assert out.count('75%') == 1
        assert out.count('SomeCms1') == 0
        assert out.count('25%') == 0

        result = self.db.fetch_one("SELECT `value` FROM hosts_info WHERE `key`='cms'")
        assert result == '[{"percent": 75, "name": "SomeCms2"}]'

        assert self.db.fetch_one("SELECT COUNT(id) FROM hosts_info") == 1
        assert (5 if self.selenium else 4) == self.db.fetch_one("SELECT COUNT(id) FROM urls")

        if not self.selenium:
            assert out.count('but limit in config')

        urls = self.db.fetch_col("SELECT url FROM urls ")
        assert len(urls) == (5 if self.selenium else 4)
        check_list = ['/files/', '/maxsize', '/a/', '/b/', '/c/'] \
            if self.selenium else ['/files/', '/a/', '/b/', '/c/']
        assert urls.sort() == check_list.sort()

        assert (6 if self.selenium else 5) == self.db.fetch_one('SELECT COUNT(id) FROM urls_base')
        assert self.db.fetch_one('SELECT COUNT(id) FROM urls_base WHERE name="/" AND host_id=1 AND parent_id=0') == 1
        assert self.db.fetch_one('SELECT COUNT(id) FROM urls_base WHERE name="a" AND host_id=1 AND parent_id=1') == 1
        if self.selenium:
            assert self.db.fetch_one(
                'SELECT COUNT(id) FROM urls_base WHERE name="maxsize" AND host_id=1 AND parent_id=1') == 1
        assert self.db.fetch_one('SELECT COUNT(id) FROM urls_base WHERE name="b" AND host_id=1 AND parent_id=1') == 1
        assert self.db.fetch_one('SELECT COUNT(id) FROM urls_base WHERE name="c" AND host_id=1 AND parent_id=1') == 1
        assert self.db.fetch_one(
            'SELECT COUNT(id) FROM urls_base WHERE name="files" AND host_id=1 AND parent_id=1') == 1

        self._check_requests_log()
        self._check_logger()


    simple_scans = [
        ('get', 'get', False),
        ('get', 'get', True),
        ('post', 'post', False),
        ('post', 'post', True),
        (None, 'head', False),
        (None, 'head', True),
    ]
    @pytest.mark.parametrize("method,check_method,use_https", simple_scans)
    def test_simple_scan(self, method, check_method, use_https):
        self.method = method
        self.check_method = check_method
        self.use_https = use_https
        self._usual_scan()


    not_found_custom_data = [
        ('--not-found-codes=301,302', ['/files/', '/a/', '/b/'], 'head', 'head'),
        ('--not-found-re=Some test phrase', ['/files/'], 'get', 'get'),
        ('--not-found-re=Some test phrase', ['/files/'], 'head', 'get')
    ]
    @pytest.mark.parametrize("not_found_param,check_urls,method,check_method", not_found_custom_data)
    def test_scan_not_found_custom(self, not_found_param, check_urls, method, check_method):
        """ Scan with custom not-found data """
        self._prepare_db()
        self.method = method
        self.check_method = check_method
        self.found_items = []
        run_params = [
            './main.py', 'test', 'Cms', 'scan', '--host=wrtest.com', '--threads=3', not_found_param
        ]
        out = self._run('normal', run_params)

        assert out.count('SomeCms2') == 0
        assert out.count('75%') == 0
        assert out.count('SomeCms1') == 0
        assert out.count('25%') == 0

        assert self.db.fetch_one("SELECT COUNT(id) FROM hosts_info") == 0

        urls = self.db.fetch_col("SELECT url FROM urls ")
        assert len(urls) == len(check_urls)
        assert urls == check_urls


    selenium_scan_protect_data = [
        (True, '--ddos-detect-phrase=PROTECTION', False),
        (True, '--ddos-detect-phrase=PROTECTION', True),
        (False, '', False),
        (True, '--ddos-human-action=PROTECTION', False),
    ]
    @pytest.mark.parametrize("use_protect,protect_param,use_https", selenium_scan_protect_data)
    def test_selenium_scan_protection(self, use_protect, protect_param, use_https):
        if use_protect:
            requests.get("http://wrtest.com/?protect_enable=1")
            run_params = ['--selenium=1', '--not-found-re=<h1>Not Found</h1>', protect_param, '--threads=1']
        else:
            run_params = ['--selenium=1', '--not-found-re=<h1>Not Found</h1>', '--threads=1']

        self.use_https = use_https
        self.selenium = True
        self.method = 'get'
        self.check_method = 'get'
        self._usual_scan(run_params)

    error_cmds = [
        (
            [
                './main.py', 'test', 'Cms', 'scan', '--host=notfound.com', '--threads=3', '--not-found-re',
                "Some test phrase", "--method=head"
            ],
            'not found in this project'
        ),
        (
            [
                './main.py', 'test', 'Cms', 'scan', '--host=wrtest.com', '--threads=3', '--protocol=test'
            ],
            'Protocol param must be '
        ),
        (
            [
                './main.py', 'test', 'Cms', 'scan', '--host=wrtest.com', '--threads=3', '--method=test'
            ],
            'Method param must be only '
        ),
        (
            [
                './main.py', 'test', 'Cms', 'scan', '--host=wrtest.com', '--threads=3', '--not-found-codes=301,a,302'
            ],
            'Not-found code must be digital, but'
        ),
        (
            [
                './main.py', 'test', 'Cms', 'scan', '--host=wrtest.com', '--threads=3', '--delay=a'
            ],
            'Delay param must be digital, but'
        ),
    ]
    @pytest.mark.parametrize("cmd_set,check_phrase", error_cmds)
    def test_error(self, cmd_set, check_phrase):
        self._prepare_db()
        out = self._run('normal', cmd_set)
        assert out.count(check_phrase)

    def test_scan_get_with_delay(self):
        """ Usual GET scan with delay """
        stime = int(time.time())
        self.method = 'get'
        self.check_method = 'get'
        self._usual_scan()
        first_time = int(time.time()) - stime

        requests.get("http://wrtest.com/?clean_log=1")

        self._prepare_db()

        stime = int(time.time())
        self.method = 'get'
        self.check_method = 'get'
        self._usual_scan(['--delay=4'])
        second_time = int(time.time()) - stime

        assert second_time/first_time >= 2
        assert second_time-first_time >= 8
