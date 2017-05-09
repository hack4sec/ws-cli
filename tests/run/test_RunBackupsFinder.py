# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Tests of BackupsFinder module
"""
import sys
import os
import time
import requests
import pytest

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
from libs.common import t, md5sum, file_get_contents, md5

class Test_RunBackupsFinder(CommonTest):
    """Tests of BackupsFinder module"""
    dirs = None
    files = None
    found_items = None
    method = None
    check_method = None
    use_https = False
    selenium = False
    requests = None

    def setup(self):
        CommonTest.setup(self)

        self.dirs = None
        self.files = None
        self.found_items = None
        self.method = None
        self.check_method = None
        self.use_https = False
        self.selenium = False
        self.requests = None

        requests.get("http://wrtest.com/?clean_log=1")
        requests.get("http://wrtest.com/?protect_disable=1")
        requests.get("http://wrtest.com/?found_disable=1")

    def _db_prepare(self, objs, reqs=None):
        reqs = reqs or None
        self.db.q("TRUNCATE TABLE `projects`")
        self.db.q("TRUNCATE TABLE `ips`")
        self.db.q("TRUNCATE TABLE `hosts`")
        self.db.q("TRUNCATE TABLE `urls`")
        self.db.q("TRUNCATE TABLE `requests`")

        self.db.q("INSERT INTO projects (id, name, descr) VALUES(1, 'test', '')")
        self.db.q("INSERT INTO ips (id, project_id, ip, descr) VALUES(1, 1, '127.0.0.1', '')")
        self.db.q("INSERT INTO `hosts` (id, project_id, ip_id, name, descr) VALUES (1,1,1,'wrtest.com', 'hd1')")

        for item in objs:
            self.db.q("INSERT INTO `urls`"
                      "(id, project_id, host_id, hash, url, referer, response_code, response_time, "
                      "size, when_add, who_add, descr, spidered)"
                      "VALUES (0, 1, 1, '{0}', '{1}', '', 0, 0, 0, 1, 'human', '', 0)".format(md5(item), item))
        if reqs:
            for item in reqs:
                self.db.q(
                    "INSERT INTO `requests` "
                    "(`id`, `hash`, `project_id`, `host_id`, `path`, "
                    "`params`, `method`, `protocol`, `founder`, `comment`) "
                    "VALUES (0, '{0}', 1, 1, '{1}', '', 'GET', 'http', 'backups', 'May be important backup')"
                    .format(item['hash'], item['item'])
                )

    def _how_many_variants(self):
        """How many variants for requests we have?"""
        files_variants = len(file_get_contents(wrpath + "/bases/bf-files.txt").strip().split("\n"))
        dirs_variants = len(file_get_contents(wrpath + "/bases/bf-dirs.txt").strip().split("\n"))
        return len(self.files)*files_variants+len(self.dirs)*dirs_variants

    def _check_logger(self):
        """Check logger work"""
        logs_path = "{0}/logs/backups/{1}/".format(wrpath, t("%Y-%m-%d"))
        time_dir = sorted(os.listdir(logs_path))[-1]

        run_log_data = file_get_contents("{0}/{1}/run.log".format(logs_path, time_dir))
        assert "Loaded {0} variants".format(self._how_many_variants()) in run_log_data
        if not self.selenium:
            for item in self.found_items:
                assert item['name'] in run_log_data
                if self.check_method is not 'head':
                    assert item['sum'] == md5sum("{0}/{1}/items/{2}".format(logs_path, time_dir, item['log']))

    def _check_requests_log(self):
        """Checking requets log from server"""
        resp = requests.get("http://wrtest.com/?get_log=1").text.strip()
        assert len(resp.split("\n")) == self._how_many_variants()

        for _str in resp.split("\n"):
            tmp_protocol, tmp_ua, tmp_method, tmp_url = _str.split("\t")
            assert tmp_method.lower() == self.check_method.lower()
            assert tmp_protocol.lower() == ('https' if self.use_https else 'http')

        tmp_list_orig = resp.split("\n")
        sorted(tmp_list_orig)
        tmp_list_uniq = list(set(resp.split("\n")))
        sorted(tmp_list_uniq)

        assert len(tmp_list_orig) == len(tmp_list_uniq)

    def _check_requests(self, found_items_names):
        """
        Check requests table fill
        :param found_items_names:
        :return:
        """
        assert len(self.found_items) == self.db.fetch_one("SELECT COUNT(id) FROM requests")

        for path in self.db.fetch_col("SELECT DISTINCT path FROM requests"):
            assert path in found_items_names

        if self.found_items:
            assert (self.check_method if self.check_method else 'head') == \
                   self.db.fetch_one("SELECT DISTINCT method FROM requests").lower()

            assert int(bool(self.found_items)) == self.db.fetch_one("SELECT COUNT(DISTINCT method) FROM requests")

    def _test_scan(self, additional_run_params=None):
        """
        Common method for scan
        :param additional_run_params:
        :return:
        """
        additional_run_params = additional_run_params or []
        self._db_prepare(self.dirs + self.files, self.requests)

        found_items_names = []
        for item in self.found_items:
            found_items_names.append(item['name'])

        run_params = [
            './main.py', 'test', 'BackupsFinder', 'scan', '--host=wrtest.com', '--threads=3'
        ]

        run_params.extend(additional_run_params)

        if self.method:
            run_params.append('--method=' + self.method)
        if self.use_https:
            run_params.append('--protocol=https')

        self._run('normal', run_params)
        self._check_requests(found_items_names)
        self._check_logger()
        self._check_requests_log()

    def _usual_scan(self, method, check_method, additional_params=None):
        """ Common method for simple tests """
        additional_params = additional_params or None
        self.method = method
        self.check_method = check_method

        self.dirs = ['/dir2/']
        self.files = ['/exists.php', '/atom.php']

        self.found_items = [
            {
                'name': u'/dir2.zip',
                'sum': 'c1fac60eb7538ed0ceb6406e5ab1c202',
                'log': 'dir2.zip.bin'
            },
            {
                'name': u'/dir2_old',
                'sum': 'b1d3458651d61acc90e0d3b233412c4f',
                'log': 'dir2_old.txt'
            },
            {
                'name': u'/exists.php.b',
                'sum': 'f54cd85a75e8c367783d23f3ec8f6688',
                'log': 'exists.php.b.txt'
            },
            {
                'name': u'/atom.php.back',
                'sum': '3e10f8c809242d3a0f94c18e7addb866',
                'log': 'atom.php.back.txt'
            },
        ]

        self._test_scan(additional_params)

    test_scan_data = [
        ('get', 'get', False),
        (None, 'head', False),
        ('get', 'get', True),
        ('post', 'post', False),
        ('post', 'post', True),
        ('head', 'head', False),
        ('head', 'head', True),
    ]
    @pytest.mark.parametrize("method,check_method,use_https", test_scan_data)
    def test_scan(self, method, check_method, use_https):
        self.use_https = use_https
        self._usual_scan(method, check_method)

    def test_scan_get_one_exists(self):
        self.requests = [{"item": "/dir2.zip", "hash": "de0874173090323da8382c8551b0e0a6"}]
        self._usual_scan('get', 'get')

    many_positives_data = [
        (False),
        (True)
    ]
    @pytest.mark.parametrize("selenium", many_positives_data)
    def test_scan_many_positives(self, selenium):
        requests.get("http://wrtest.com/?found_enable=1")

        self.dirs = ['/dir0/', '/dir1/', '/dir2/', '/dir3/', '/dir4/', '/dir5/', '/dir6/', '/dir7/']
        self.files = ['/exists.php', '/atom.php', '/1.php', '/2.php', '/3.php', '/4.php', '/5.php']

        self._db_prepare(self.dirs + self.files)

        run_params = [
            './main.py', 'test', 'BackupsFinder', 'scan', '--host=wrtest.com', '--threads=2',
            '--not-found-re=aaaaaaaaaaaaaaaa'
        ]

        if selenium:
            run_params.append('--selenium=1')

        out = self._run('many-positives', run_params)
        assert 'Many positive detections' in out
        assert self.db.fetch_one("SELECT COUNT(id) FROM requests") == 0

    selenium_scan_protect_data = [
        (True, '--ddos-detect-phrase=PROTECTION', False),
        (True, '--ddos-detect-phrase=PROTECTION', True),
        (False, '', False),
        (True, '--ddos-human-action=PROTECTION', False),
        (True, '--ddos-human-action=PROTECTION', True),
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

        self.dirs = ['/dir2/']
        self.files = ['/exists.php', '/atom.php']
        self.found_items = [
            {
                'name': u'/dir2.zip',
                'sum': 'c1fac60eb7538ed0ceb6406e5ab1c202',
                'log': 'dir2.zip.bin'
            },
            {
                'name': u'/dir2_old',
                'sum': 'b1d3458651d61acc90e0d3b233412c4f',
                'log': 'dir2_old.txt'
            },
            {
                'name': u'/exists.php.b',
                'sum': 'f54cd85a75e8c367783d23f3ec8f6688',
                'log': 'exists.php.b.txt'
            },
            {
                'name': u'/atom.php.back',
                'sum': '3e10f8c809242d3a0f94c18e7addb866',
                'log': 'atom.php.back.txt'
            },
        ]
        self._test_scan(run_params)


    def test_scan_max_size(self):
        """ Check what if object have a size more then max (from config) """
        self._db_prepare(['/dir3/'])

        out = self._run('normal', [
            './main.py', 'test', 'BackupsFinder', 'scan', '--host=wrtest.com',
            '--threads=3', '--not-found-re', "Some test phrase"
        ])
        assert 'but limit in config' in out

        assert self.db.fetch_one("SELECT COUNT(id) FROM requests") == 0

        out = self._run('bf-max-size-big', [
            './main.py', 'test', 'BackupsFinder', 'scan', '--host=wrtest.com',
            '--threads=3', '--not-found-re', "Some test phrase"
        ])
        assert 'but limit in config' not in out

        assert self.db.fetch_one("SELECT COUNT(id) FROM requests") == 1

    def test_scan_get_with_delay(self):
        """ Usual GET scan with delay """
        stime = int(time.time())
        self._usual_scan('get', 'get')
        first_time = int(time.time()) - stime

        requests.get("http://wrtest.com/?clean_log=1")

        stime = int(time.time())
        self._usual_scan('get', 'get', ['--delay=2'])
        second_time = int(time.time()) - stime

        assert second_time/first_time >= 3

    def test_scan_get_with_not_found_phrase(self):
        """ GET scan with not-found-re param """

        # First - usual scan and found 1 link
        self.method = 'head'
        self.check_method = 'head'

        self.dirs = []
        self.files = ['/404-phrase.php']

        self.found_items = [
            {
                'name': u'/404-phrase.php.old',
                'sum': '',
                'log': '404-phrase.php.old.txt'
            },
        ]

        self._test_scan()

        # Scan with --not-found-re
        self.method = 'head'
        self.check_method = 'get'

        self.dirs = []
        self.files = ['/404-phrase.php']

        self.found_items = []

        requests.get("http://wrtest.com/?clean_log=1")

        self._test_scan(['--not-found-re=Some test phrase'])

    errors_data = [
        (
            [
                './main.py', 'test', 'BackupsFinder', 'scan', '--host=notfound.com', '--threads=3', '--not-found-re',
                "Some test phrase"
            ],
            'not found in this project'
        ),
        (
            [
                './main.py', 'test', 'BackupsFinder', 'scan', '--host=wrtest.com', '--protocol=test',
                '--threads=3', '--not-found-re', "Some test phrase"
            ],
            'Protocol param must be '
        ),
        (
            [
                './main.py', 'test', 'BackupsFinder', 'scan', '--host=wrtest.com', '--method=test', '--threads=3',
                '--not-found-re', "Some test phrase"
            ],
            'Method param must be only '
        ),
        (
            [
                './main.py', 'test', 'BackupsFinder', 'scan', '--host=wrtest.com', '--threads=3',
                '--not-found-codes', "300,a,400"
            ],
            'Not-found code must be digital, but'
        ),
        (
            [
                './main.py', 'test', 'BackupsFinder', 'scan', '--host=wrtest.com', '--threads=3',
                '--proxies', "/not/found"
            ],
            'Proxy list not found'
        ),
        (
            [
                './main.py', 'test', 'BackupsFinder', 'scan', '--host=wrtest.com', '--threads=3', '--delay=a'
            ],
            'Delay param must be digital, but'
        ),
    ]
    @pytest.mark.parametrize("cmd_set,check_phrase", errors_data)
    def test_error(self, cmd_set, check_phrase):
        self._db_prepare([])
        out = self._run('normal', cmd_set)
        assert out.count(check_phrase)
