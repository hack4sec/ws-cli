# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Tests of FuzzerUrls module
"""
import sys
import os
import subprocess
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


class Test_RunFuzzerUrls(CommonTest):
    """Tests of FuzzerUrls module"""
    def setup(self):
        CommonTest.setup(self)

        requests.get("http://wrtest.com/?clean_log=1")
        requests.get("http://wrtest.com/?protect_disable=1")
        requests.get("http://wrtest.com/?found_disable=1")

    def _prepare_db(self):
        self.db.q("INSERT INTO projects (id, name, descr) VALUES(1, 'test', '')")
        self.db.q("INSERT INTO ips (id, project_id, ip, descr) VALUES(1, 1, '127.0.0.1', '')")
        self.db.q("INSERT INTO `hosts` (id, project_id, ip_id, name, descr) VALUES (1,1,1,'wrtest.com', 'hd1')")

    scan_data = [
        ('http'),
        ('https')
    ]
    @pytest.mark.parametrize("protocol", scan_data)
    def test_scan(self, protocol):
        self._prepare_db()
        self.db.q("INSERT INTO `urls`"
                  "(id, project_id, host_id, hash, url, referer, response_code, response_time, "
                  "size, when_add, who_add, descr, spidered)"
                  "VALUES(1, 1, 1, '6666cd76f96956469e7be39d750cc7d9', "
                  "'/fuzz.php?a=1&b=2', '', 0, 0, 0, 1, 'human', '', 0),"
                  "(3, 1, 1, '6666cd76f96k56469e7be39d750cc7d9', '/fuzz-500.php?c=1', '', 0, 0, 0, 1, 'human', '', 0),"
                  "(2, 1, 1, '6666cd76f96956469e7be39d750cc7d8', '/maxsize?a=1', '', 0, 0, 0, 1, 'human', '', 0)")

        assert self.db.fetch_one("SELECT COUNT(id) FROM requests") == 0

        out = self._run('normal', [
            './main.py', 'test', 'FuzzerUrls', 'scan', '--host=wrtest.com', '--threads=3', '--protocol=' + protocol
        ])

        assert bool(out.count('but limit in config'))
        assert self.db.fetch_one("SELECT COUNT(id) FROM requests") == 6
        assert self.db.fetch_one("SELECT COUNT(id) FROM requests WHERE path='/fuzz.php'") == 4
        assert self.db.fetch_one("SELECT COUNT(id) FROM requests WHERE path='/fuzz-500.php'") == 2
        check_list = ['a[]=1&b=2&', 'a[][]=1&b=2&', 'a=1&b[][]=2&', 'a=1&b[]=2&', 'c[]=1&', 'c[][]=1&']
        for params in self.db.fetch_col("SELECT params FROM requests"):
            assert params in check_list
            check_list.remove(params)

    error_cmds = [
        (
            [
                './main.py', 'test', 'FuzzerUrls', 'scan', '--host=notfound.com', '--threads=3', "--method=head"
            ],
            'not found in this project'
        ),
        (
            [
                './main.py', 'test', 'FuzzerUrls', 'scan', '--host=wrtest.com', '--threads=3', '--protocol=test'
            ],
            'Protocol param must be '
        ),
        (
            [
                './main.py', 'test', 'FuzzerUrls', 'scan', '--host=wrtest.com', '--threads=3', '--method=test'
            ],
            'Method param must be only '
        )
    ]

    @pytest.mark.parametrize("cmd_set,check_phrase", error_cmds)
    def test_error(self, cmd_set, check_phrase):
        self._prepare_db()
        out = self._run('normal', cmd_set)
        assert out.count(check_phrase)

    def test_scan_selenium(self):
        self.db.q("INSERT INTO projects (id, name, descr) VALUES(1, 'test', '')")
        self.db.q("INSERT INTO ips (id, project_id, ip, descr) VALUES(1, 1, '127.0.0.1', '')")
        self.db.q("INSERT INTO `hosts` (id, project_id, ip_id, name, descr) VALUES (1,1,1,'wrtest.com', 'hd1')")
        self.db.q("INSERT INTO `urls`"
                  "(id, project_id, host_id, hash, url, referer, response_code, response_time, "
                  "size, when_add, who_add, descr, spidered)"
                  "VALUES(1, 1, 1, '6666cd76f96956469e7be39d750cc7d9', "
                  "'/fuzz.php?a=1&b=2', '', 0, 0, 0, 1, 'human', '', 0),"
                  "(3, 1, 1, '6666cd76f96k56469e7be39d750cc7d9', '/fuzz-500.php?c=1', '', 0, 0, 0, 1, 'human', '', 0),"
                  "(2, 1, 1, '6666cd76f96956469e7be39d750cc7d8', '/maxsize?a=1', '', 0, 0, 0, 1, 'human', '', 0)")

        assert self.db.fetch_one("SELECT COUNT(id) FROM requests") == 0

        self._replace_config('normal')
        os.chdir(wrpath)
        out = subprocess.check_output([
            './main.py', 'test', 'FuzzerUrls', 'scan', '--host=wrtest.com', '--threads=1', '--selenium=1',
            '--ddos-detect-phrase', 'somephrasenotexists'
        ])
        self._restore_config()
        self.output_errors(out)

        assert self.db.fetch_one("SELECT COUNT(id) FROM requests") == 4
        assert self.db.fetch_one("SELECT COUNT(id) FROM requests WHERE path='/fuzz.php'") == 4

        assert self.db.fetch_one("SELECT COUNT(id) FROM requests WHERE path='/fuzz-500.php'") == 0
        check_list = ['a[]=1&b=2&', 'a[][]=1&b=2&', 'a=1&b[][]=2&', 'a=1&b[]=2&', 'c[]=1&', 'c[][]=1&']
        for params in self.db.fetch_col("SELECT params FROM requests"):
            assert params in check_list
            check_list.remove(params)
