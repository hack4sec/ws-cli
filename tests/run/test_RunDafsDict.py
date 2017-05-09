# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Tests of DafsDict module
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

class Test_RunDafsDict(CommonTest):
    """Tests of DafsDict module"""
    method = None
    check_method = None
    use_https = False
    selenium = False
    dict = None

    def setup(self):
        CommonTest.setup(self)

        self.method = None
        self.check_method = None
        self.use_https = False
        self.selenium = False
        self.dict = None

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

    def _logger_dirs(self, content=True):
        """Check logger work for dirs"""
        logs_path = "{0}/logs/dafs/{1}/".format(wrpath, t("%Y-%m-%d"))
        time_dir = sorted(os.listdir(logs_path))[-1]

        run_log_data = file_get_contents("{0}/{1}/run.log".format(logs_path, time_dir))
        assert "Loaded {0} words from source".format(self._how_many_variants()) in run_log_data
        assert "/dir1/" in run_log_data
        assert "/dir2/" in run_log_data

        for item in ['aaa', 'bbb', 'ccc', 'ddd']:
            assert os.path.exists("{0}/{1}/items/{2}.txt".format(logs_path, time_dir, item))
            if self.check_method != 'head':
                assert ('<h1>Not Found</h1>' if content else '') in \
                       file_get_contents("{0}/{1}/items/{2}.txt".format(logs_path, time_dir, item))

        for item in ['dir1', 'dir2']:
            assert os.path.exists("{0}/{1}/items/{2}.txt".format(logs_path, time_dir, item))
            if self.check_method != 'head':
                assert '<h1>Not Found</h1>' not in \
                       file_get_contents("{0}/{1}/items/{2}.txt".format(logs_path, time_dir, item))

    def _logger_files(self, content=True, good_items=None):
        """Check logger work for files"""
        good_items = good_items or ['atom.php', 'index.php', 'aaa.php', 'redirect.php']

        logs_path = "{0}/logs/dafs/{1}/".format(wrpath, t("%Y-%m-%d"))
        time_dir = sorted(os.listdir(logs_path))[-1]

        run_log_data = file_get_contents("{0}/{1}/run.log".format(logs_path, time_dir))
        assert "Loaded {0} words from source".format(self._how_many_variants()) in run_log_data
        for item in good_items:
            assert item in run_log_data

        for item in ['lll.eee', 'test.txt', 'aaa.bbb', 'wtf.php']:
            assert os.path.exists("{0}/{1}/items/{2}.txt".format(logs_path, time_dir, item))
            if self.check_method != 'head':
                assert ('<h1>Not Found</h1>' if content else '') in \
                       file_get_contents("{0}/{1}/items/{2}.txt".format(logs_path, time_dir, item))

        for item in good_items:
            assert os.path.exists("{0}/{1}/items/{2}.txt".format(logs_path, time_dir, item))
            assert item in run_log_data
            if self.check_method != 'head':
                assert '<h1>Not Found</h1>' not in \
                       file_get_contents("{0}/{1}/items/{2}.txt".format(logs_path, time_dir, item))

    def _how_many_variants(self):
        """How many variants for requests we have?"""
        return len(open(self.dict).read().strip().split("\n"))

    def _check_requests_log(self, selenium_files = False):
        """Checking requets log from server"""
        resp = requests.get("http://wrtest.com/?get_log=1").text.strip()
        # Selenium make 5 other requests - redirect to roos and css/js from there
        if selenium_files:
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
        ('dirs', 'get', 'get', False, '@'),
        ('dirs', 'get', 'get', True, '@'),
        ('dirs', 'post', 'post', False, '@'),
        ('dirs', 'post', 'post', True, '@'),
        ('dirs', 'head', 'head', False, '@'),
        ('dirs', 'head', 'head', True, '@'),
        ('dirs', False, 'head', False, '@'),
        ('dirs', False, 'head', True, '@'),
        ('dirs', 'get', 'get', False, '%'),
        ('files', 'get', 'get', False, '@'),
        ('files', 'get', 'get', True, '@'),
        ('files', 'post', 'post', False, '@'),
        ('files', 'post', 'post', True, '@'),
        ('files', 'head', 'head', False, '@'),
        ('files', 'head', 'head', True, '@'),
        ('files', False, 'head', False, '@'),
        ('files', False, 'head', True, '@'),
        ('files', 'get', 'get', False, '%'),
    ]
    @pytest.mark.parametrize("objs_type,method,check_method,use_https,msymbol", test_scan_dirs_data)
    def test_scan(self, objs_type, method, check_method, use_https, msymbol):
        self._prepare_db()
        self.use_https = use_https
        self.check_method = check_method
        self.dict = 'tests/run/files/dafs-' + objs_type + '.txt'

        run_params = [
            './main.py', 'test', 'DafsDict', 'scan', '--host=wrtest.com',
            '--dict=' + self.dict,
        ]
        if method:
            run_params.append('--method=' + method)
        if use_https:
            run_params.append('--protocol=https')
        if msymbol != '@':
            run_params.append('--msymbol=' + msymbol)

        run_params.append('--template=/' + msymbol + ('/' if objs_type == 'dirs' else ''))

        self._run('normal', run_params)

        if objs_type == 'dirs':
            assert self.db.fetch_one("SELECT COUNT(id) FROM urls") == 3
            assert self.db.fetch_one("SELECT COUNT(id) FROM urls_base") == 3
            assert self.db.fetch_one(
                "SELECT COUNT(id) FROM urls_base WHERE name='dir1' AND parent_id=1 AND host_id=1") == 1
            assert self.db.fetch_one(
                "SELECT COUNT(id) FROM urls_base WHERE name='dir2' AND parent_id=1 AND host_id=1") == 1
            assert self.db.fetch_one(
                "SELECT COUNT(id) FROM urls_base WHERE name='/' AND parent_id=0 AND host_id=1") == 1
        else:
            assert self.db.fetch_one("SELECT COUNT(id) FROM urls") == 6

        if objs_type == 'files':
            self._logger_files()
        else:
            self._logger_dirs()
        self._check_requests_log()

    many_positives_data = [
        (False),
        (True)
    ]
    @pytest.mark.parametrize("selenium", many_positives_data)
    def test_scan_many_positives(self, selenium):
        requests.get("http://wrtest.com/?found_enable=1")

        self._prepare_db()
        self.check_method = 'get'
        self.dict = 'tests/run/files/dafs-mp.txt'

        run_params = [
            './main.py', 'test', 'DafsDict', 'scan', '--host=wrtest.com', '--template=/@/',
            '--dict=' + self.dict, '--not-found-re=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        ]
        if selenium:
            run_params.append('--selenium=1')
            run_params.append('--threads=1')
        out = self._run('many-positives', run_params)

        assert 'Many positive detections' in out
        assert self.db.fetch_one("SELECT COUNT(id) FROM urls") == 0

    def test_scan_with_delay(self):
        self._prepare_db()

        stime = int(time.time())
        self._run('normal', [
            './main.py', 'test', 'DafsDict', 'scan', '--host=wrtest.com', '--template=/@/',
            '--dict=tests/run/files/dafs-files.txt', '--threads=1'
        ])
        first_time = int(time.time()) - stime
        time.sleep(1)
        stime = int(time.time())
        self._run('normal', [
            './main.py', 'test', 'DafsDict', 'scan', '--host=wrtest.com', '--template=/@/',
            '--dict=tests/run/files/dafs-files.txt', '--delay=2', '--threads=1'
        ])
        second_time = int(time.time()) - stime
        assert second_time/first_time >= 4

    def test_scan_dirs_deep(self):
        """ Usual GET scan on dirs, deep - 2 """
        self._prepare_db()
        self.check_method = 'get'
        self.dict = 'tests/run/files/dafs-dirs.txt'
        self._run('normal', [
            './main.py', 'test', 'DafsDict', 'scan', '--host=wrtest.com', '--template=/deep/moredeep/@/',
            '--dict=tests/run/files/dafs-dirs.txt', '--method=GET'
        ])
        assert self.db.fetch_one("SELECT COUNT(id) FROM urls") == 5
        assert self.db.fetch_one("SELECT COUNT(id) FROM urls WHERE url='/deep/moredeep/dir1/'") == 1
        assert self.db.fetch_one("SELECT COUNT(id) FROM urls WHERE url='/deep/moredeep/dir2/'") == 1
        assert self.db.fetch_one("SELECT COUNT(id) FROM urls_base") == 5
        assert self.db.fetch_one("SELECT COUNT(id) FROM urls_base WHERE name='/' AND parent_id=0 AND host_id=1") == 1
        assert self.db.fetch_one("SELECT COUNT(id) FROM urls_base WHERE name='deep' AND parent_id=1 AND host_id=1") == 1
        assert self.db.fetch_one(
            "SELECT COUNT(id) FROM urls_base WHERE name='moredeep' AND parent_id=2 AND host_id=1") == 1
        assert self.db.fetch_one("SELECT COUNT(id) FROM urls_base WHERE name='dir1' AND parent_id=3 AND host_id=1") == 1
        assert self.db.fetch_one("SELECT COUNT(id) FROM urls_base WHERE name='dir2' AND parent_id=3 AND host_id=1") == 1

        self._logger_dirs()
        self._check_requests_log()

    selenium_scan_protect_data = [
        ('files', True, '--ddos-detect-phrase=PROTECTION', False),
        ('files', True, '--ddos-detect-phrase=PROTECTION', True),
        ('files', False, '', False),
        ('files', True, '--ddos-human-action=PROTECTION', False),
        ('dirs', True, '--ddos-detect-phrase=PROTECTION', False),
        ('dirs', True, '--ddos-detect-phrase=PROTECTION', True),
        ('dirs', False, '', False),
        ('dirs', True, '--ddos-human-action=PROTECTION', False),
    ]
    @pytest.mark.parametrize("objs_type,use_protect,protect_param,use_https", selenium_scan_protect_data)
    def test_selenium_scan_protection(self, objs_type, use_protect, protect_param, use_https):
        self._prepare_db()
        self.check_method = 'get'
        self.selenium = True
        self.use_https = use_https
        self.dict = 'tests/run/files/dafs-' + objs_type + '.txt'

        run_params = [
            './main.py', 'test', 'DafsDict', 'scan', '--host=wrtest.com',
            '--template=/@' + ('/' if objs_type == 'dirs' else ''),
            '--dict=' + self.dict,
            '--selenium=1', '--threads=1', '--not-found-re=Not Found'
        ]
        if use_protect:
            requests.get("http://wrtest.com/?protect_enable=1")
            run_params.append(protect_param)
        if use_https:
            run_params.append('--protocol=https')

        self._run('normal', run_params)
        assert self.db.fetch_one("SELECT COUNT(id) FROM urls") == (7 if objs_type == 'files' else 3)

    not_found_custom_data = [
        ('--not-found-codes=301,302', ['aaa.php', 'index.php'], 'head', 'head'),
        ('--not-found-re=aaa', ['atom.php', 'index.php', 'redirect.php'], 'get', 'get'),
        ('--not-found-re=aaa', ['atom.php', 'index.php', 'redirect.php'], 'head', 'get'),
    ]
    @pytest.mark.parametrize("not_found_param,check_urls,method,check_method", not_found_custom_data)
    def test_scan_not_found_custom(self, not_found_param, check_urls, method, check_method):
        self._prepare_db()
        self.check_method = check_method
        self.dict = 'tests/run/files/dafs-files.txt'
        out = self._run('normal', [
            './main.py', 'test', 'DafsDict', 'scan', '--host=wrtest.com', '--template=/@',
            '--dict=tests/run/files/dafs-files.txt', '--method=' + method, not_found_param
        ])
        assert bool(out.count("but limit in config"))
        assert self.db.fetch_one("SELECT COUNT(id) FROM urls") == 5

        self._logger_files(good_items=check_urls)
        self._check_requests_log()


    error_cmds = [
        (
            [
                './main.py', 'test', 'DafsDict', 'scan', '--host=wrtest.com', '--template=/@',
                '--dict=notfound.txt', '--method=HEAD'
            ],
            'not exists or not readable'
        ),
        (
            [
                './main.py', 'test', 'DafsDict', 'scan', '--host=notfound.com', '--template=/@',
                '--dict=tests/run/files/dafs-dirs.txt', '--method=HEAD'
            ],
            'not found in this project'
        ),
        (
            [
                './main.py', 'test', 'DafsDict', 'scan', '--host=wrtest.com', '--template=/@',
                '--dict=tests/run/files/dafs-dirs.txt', '--protocol=test'
            ],
            'Protocol param must be '
        ),
        (
            [
                './main.py', 'test', 'DafsDict', 'scan', '--host=wrtest.com',
                '--template=/@', '--dict=tests/run/files/dafs-dirs.txt', '--method=test'
            ],
            'Method param must be only '
        ),
        (
            [
                './main.py', 'test', 'DafsDict', 'scan', '--host=wrtest.com', '--template=/@',
                '--dict=tests/run/files/dafs-dirs.txt', '--not-found-codes=301,a,302'
            ],
            'Not-found code must be digital, but'
        ),
        (
            [
                './main.py', 'test', 'DafsDict', 'scan', '--host=wrtest.com', '--template=/@',
                '--dict=tests/run/files/dafs-dirs.txt', '--parts=a', '--part=1'
            ],
            'Parts param must be digital, but'
        ),
        (
            [
                './main.py', 'test', 'DafsDict', 'scan', '--host=wrtest.com', '--template=/@',
                '--dict=tests/run/files/dafs-dirs.txt', '--part=a', '--parts=2'
            ],
            'Part param must be digital, but'
        ),
        (
            [
                './main.py', 'test', 'DafsDict', 'scan', '--host=wrtest.com', '--template=/@',
                '--dict=tests/run/files/dafs-dirs.txt', '--part=1'
            ],
            "If you use '--part' param, you must specify '--parts'"
        ),
        (
            [
                './main.py', 'test', 'DafsDict', 'scan', '--host=wrtest.com', '--template=/@',
                '--dict=tests/run/files/dafs-dirs.txt', '--parts=1'
            ],
            "If you use '--parts' param, you must specify '--part'"
        ),
        (
            [
                './main.py', 'test', 'DafsDict', 'scan', '--host=wrtest.com', '--template=/@',
                '--dict=tests/run/files/dafs-dirs.txt', '--parts=1', '--part=2'
            ],
            'Number of part'
        ),
        (
            [
                './main.py', 'test', 'DafsDict', 'scan', '--host=wrtest.com', '--template=/@',
                '--dict=tests/run/files/dafs-dirs.txt', '--delay=a'
            ],
            'Delay param must be digital, but'
        ),
    ]
    @pytest.mark.parametrize("cmd_set,check_phrase", error_cmds)
    def test_error(self, cmd_set, check_phrase):
        self._prepare_db()
        out = self._run('normal', cmd_set)
        assert out.count(check_phrase)
