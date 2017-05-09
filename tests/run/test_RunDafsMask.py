# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Tests of DafsMask module
"""
import sys
import os
import time
import pytest
import requests
from libs.common import file_get_contents, t

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


class Test_RunDafsMask(CommonTest):
    """Tests of DafsMask module"""
    method = None
    check_method = None
    use_https = False
    selenium = False
    dict = None
    mask = None
    masks = {'?l': 26}

    def setup(self):
        CommonTest.setup(self)

        self.method = None
        self.check_method = None
        self.use_https = False
        self.selenium = False
        self.dict = None
        self.mask = None

        requests.get("http://wrtest.com/?clean_log=1")
        requests.get("http://wrtest.com/?protect_disable=1")
        requests.get("http://wrtest.com/?found_disable=1")

    def _prepare_db(self):
        self.db.q("TRUNCATE TABLE `projects`")
        self.db.q("TRUNCATE TABLE `ips`")
        self.db.q("TRUNCATE TABLE `hosts`")
        self.db.q("TRUNCATE TABLE `hosts_info`")
        self.db.q("TRUNCATE TABLE `urls`")
        self.db.q("TRUNCATE TABLE `requests`")
        self.db.q("INSERT INTO projects (id, name, descr) VALUES(1, 'test', '')")
        self.db.q("INSERT INTO ips (id, project_id, ip, descr) VALUES(1, 1, '127.0.0.1', '')")
        self.db.q("INSERT INTO `hosts` (id, project_id, ip_id, name, descr) VALUES (1,1,1,'wrtest.com', 'hd1')")

    def _logger(self, content=True, good_items=None, bad_items=None, in_output=None):
        """
        Check logger work
        :param content: We check content?
        :param good_items: This items was found
        :param bad_items: This items was not found
        :param in_output: check this phrases in output
        :return:
        """
        good_items = good_items or []
        bad_items = bad_items or []
        in_output = in_output or []

        logs_path = "{0}/logs/dafs/{1}/".format(wrpath, t("%Y-%m-%d"))
        time_dir = sorted(os.listdir(logs_path))[-1]

        run_log_data = file_get_contents("{0}/{1}/run.log".format(logs_path, time_dir))

        assert "Loaded {0} words from source".format(self._how_many_variants()) in run_log_data
        for item in in_output:
            assert item in run_log_data

        for item in bad_items:
            assert os.path.exists("{0}/{1}/items/{2}.txt".format(logs_path, time_dir, item))
            if self.check_method != 'head':
                assert ('<h1>Not Found</h1>' if content else '') in \
                       file_get_contents("{0}/{1}/items/{2}.txt".format(logs_path, time_dir, item))

        for item in good_items:
            assert os.path.exists("{0}/{1}/items/{2}.txt".format(logs_path, time_dir, item))
            if self.check_method != 'head':
                assert '<h1>Not Found</h1>' not in \
                       file_get_contents("{0}/{1}/items/{2}.txt".format(logs_path, time_dir, item))

    def _how_many_variants(self):
        """How many variants for requests we have?"""
        return self.masks[self.mask]

    def _check_requests_log(self, selenium_results=False):
        """
        Check requests log from server
        :param selenium_results: we checking selenium results?
        :return:
        """
        resp = requests.get("http://wrtest.com/?get_log=1").text.strip()
        # Selenium make 5 other requests - redirect to roos and css/js from there
        if selenium_results:
            assert len(resp.split("\n")) == \
                   (self._how_many_variants() if not self.selenium else self._how_many_variants() + 5)
        else:
            assert len(resp.split("\n")) == self._how_many_variants()

        for _str in resp.split("\n"):
            tmp_protocol, tmp_ua, tmp_method, tmp_url = _str.split("\t")
            assert tmp_method.lower() == self.check_method.lower()
            assert tmp_protocol.lower() == ('https' if self.use_https else 'http')

        # No dups
        assert len(resp.split("\n")) == len(resp.split("\n"))

    test_scan_dirs_data = [
        ('get', 'get', False, '@', False),
        ('get', 'get', True, '@', False),
        ('post', 'post', False, '@', False),
        ('post', 'post', True, '@', False),
        ('head', 'head', False, '@', False),
        ('head', 'head', True, '@', False),
        (False, 'head', False, '@', False),
        (False, 'head', True, '@', False),
        ('get', 'get', False, '%', False),
        ('head', 'get', True, '@', '--not-found-re=aaa'),
    ]
    @pytest.mark.parametrize("method,check_method,use_https,msymbol,not_found_re", test_scan_dirs_data)
    def test_scan(self, method, check_method, use_https, msymbol, not_found_re):
        self._prepare_db()
        self.use_https = use_https
        self.check_method = check_method
        self.mask = '?l'

        run_params = [
            './main.py', 'test', 'DafsMask', 'scan', '--host=wrtest.com', '--mask=' + self.mask
        ]
        if method:
            run_params.append('--method=' + method)
        if not_found_re:
            run_params.append(not_found_re)
        if use_https:
            run_params.append('--protocol=https')
        if msymbol != '@':
            run_params.append('--msymbol=' + msymbol)
            run_params.append('--template=/' + msymbol + '/')
        else:
            run_params.append('--template=/@/')

        self._run('normal', run_params)

        assert self.db.fetch_one("SELECT COUNT(id) FROM urls") == 4
        test_urls = ['/a/', '/b/', '/c/']
        have_urls = self.db.fetch_col("SELECT url FROM urls")
        for test_url in test_urls:
            assert test_url in have_urls

        assert self.db.fetch_one("SELECT COUNT(id) FROM urls") == 4
        assert self.db.fetch_one("SELECT COUNT(id) FROM urls_base") == 4
        assert self.db.fetch_one("SELECT COUNT(id) FROM urls_base WHERE name='c' AND parent_id=1 AND host_id=1") == 1
        assert self.db.fetch_one("SELECT COUNT(id) FROM urls_base WHERE name='b' AND parent_id=1 AND host_id=1") == 1
        assert self.db.fetch_one("SELECT COUNT(id) FROM urls_base WHERE name='a' AND parent_id=1 AND host_id=1") == 1
        assert self.db.fetch_one("SELECT COUNT(id) FROM urls_base WHERE name='/' AND parent_id=0 AND host_id=1") == 1

        self._logger(good_items=['a', 'b', 'c'], bad_items=['d', 'e', 'f'], in_output=['/a/', '/b/', '/c/'])
        self._check_requests_log()

    def test_scan_maxsize_error_head(self):
        self._prepare_db()
        out = self._run('normal', [
            './main.py', 'test', 'DafsMask', 'scan', '--host=wrtest.com',
            '--template=/@', '--mask=maxsize', '--method=head'
        ])
        assert bool(out.count('but limit in config'))

        assert self.db.fetch_one("SELECT COUNT(id) FROM urls") == 0        

    def test_scan_with_delay(self):
        self._prepare_db()
        self._prepare_db()
        self.check_method = 'head'
        self.mask = '?l'

        stime = int(time.time())
        self._run('normal', [
            './main.py', 'test', 'DafsMask', 'scan', '--host=wrtest.com', '--template=/@/', '--mask=' + self.mask,
        ])
        first_time = int(time.time()) - stime
        time.sleep(1)
        stime = int(time.time())
        self._run('normal', [
            './main.py', 'test', 'DafsMask', 'scan', '--host=wrtest.com', '--template=/@/', '--mask=' + self.mask,
            '--threads=1', '--delay=2'
        ])
        second_time = int(time.time()) - stime
        assert second_time/first_time >= 3

    many_positives_data = [
        (False),
        (True)
    ]
    @pytest.mark.parametrize("selenium", many_positives_data)
    def test_scan_many_positives(self, selenium):
        """ Usual GET scan on dirs HEAD method with many positives process die """
        requests.get("http://wrtest.com/?found_enable=1")

        self._prepare_db()
        self.check_method = 'get'
        self.mask = '?l'

        run_params = [
            './main.py', 'test', 'DafsMask', 'scan', '--host=wrtest.com', '--template=/@/', '--mask=' + self.mask,
        ]
        if selenium:
            run_params.append('--selenium=1')
            run_params.append('--not-found-re=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
            run_params.append('--threads=1')

        out = self._run('many-positives', run_params)

        assert 'Many positive detections' in out
        assert self.db.fetch_one("SELECT COUNT(id) FROM urls") == 0

    selenium_scan_protect_data = [
        (True, '--ddos-detect-phrase=PROTECTION', False),
        (True, '--ddos-detect-phrase=PROTECTION', True),
        (False, '', False),
        (True, '--ddos-human-action=PROTECTION', False),
    ]
    @pytest.mark.parametrize("use_protect,protect_param,use_https", selenium_scan_protect_data)
    def test_selenium_scan_protection(self, use_protect, protect_param, use_https):
        self._prepare_db()
        self.check_method = 'get'
        self.selenium = True
        self.use_https = use_https
        self.mask = '?l'

        run_params = [
            './main.py', 'test', 'DafsMask', 'scan', '--host=wrtest.com',
            '--template=/@/',
            '--mask=' + self.mask,
            '--selenium=1', '--threads=1', '--not-found-re=Not Found'
        ]
        if use_protect:
            requests.get("http://wrtest.com/?protect_enable=1")
            run_params.append(protect_param)
        if use_https:
            run_params.append('--protocol=https')

        self._run('normal', run_params)
        assert self.db.fetch_one("SELECT COUNT(id) FROM urls") == 4

        self._logger(good_items=['a', 'b', 'c'], bad_items=['d', 'e', 'f'], in_output=['/a/', '/b/', '/c/'])
        self._check_requests_log(selenium_results=True)

    error_cmds = [
        (
            [
                './main.py', 'test', 'DafsMask', 'scan', '--host=notfound.com', '--template=/@',
                '--mask=l', '--method=HEAD'
            ],
            'not found in this project'
        ),
        (
            [
                './main.py', 'test', 'DafsMask', 'scan', '--host=wrtest.com', '--template=/@',
                '--mask=l', '--protocol=test'
            ],
            'Protocol param must be '
        ),
        (
            [
                './main.py', 'test', 'DafsMask', 'scan', '--host=wrtest.com',
                '--template=/@', '--mask=l', '--method=test'
            ],
            'Method param must be only '
        ),
        (
            [
                './main.py', 'test', 'DafsMask', 'scan', '--host=wrtest.com',
                '--template=/@', '--mask=l', '--not-found-codes=301,a,302'
            ],
            'Not-found code must be digital, but'
        ),
        (
            [
                './main.py', 'test', 'DafsMask', 'scan', '--host=wrtest.com', '--template=/@',
                '--mask=l', '--parts=a', '--part=1'
            ],
            'Parts param must be digital, but'
        ),
        (
            [
                './main.py', 'test', 'DafsMask', 'scan', '--host=wrtest.com', '--template=/@',
                '--mask=l', '--part=a', '--parts=2'
            ],
            'Part param must be digital, but'
        ),
        (
            [
                './main.py', 'test', 'DafsMask', 'scan', '--host=wrtest.com', '--template=/@',
                '--mask=l', '--part=1'
            ],
            "If you use '--part' param, you must specify '--parts'"
        ),
        (
            [
                './main.py', 'test', 'DafsMask', 'scan', '--host=wrtest.com', '--template=/@',
                '--mask=l', '--parts=1'
            ],
            "If you use '--parts' param, you must specify '--part'"
        ),
        (
            [
                './main.py', 'test', 'DafsMask', 'scan', '--host=wrtest.com', '--template=/@',
                '--mask=l', '--parts=1', '--part=2'
            ],
            'Number of part'
        ),
        (
            [
                './main.py', 'test', 'DafsMask', 'scan', '--host=wrtest.com', '--template=/@',
                '--mask=l', '--delay=a'
            ],
            'Delay param must be digital, but'
        ),
    ]
    @pytest.mark.parametrize("cmd_set,check_phrase", error_cmds)
    def test_error(self, cmd_set, check_phrase):
        self._prepare_db()
        out = self._run('normal', cmd_set)
        assert out.count(check_phrase)
