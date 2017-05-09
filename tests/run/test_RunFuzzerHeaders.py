# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Tests of FuzzerHeaders module
"""
import sys
import os
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


class Test_RunFuzzerHeaders(CommonTest):
    """Tests of FuzzerHeaders module"""
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
                  "VALUES (1, 1, 1, '6666cd76f96956469e7be39d750cc7d9', "
                  "'/fuzz-h.php?a=1&b=2', '', 0, 0, 0, 1, 'human', '', 0),"
                  "(3, 1, 1, '6666cd76f96k56469e7be39d750cc7d9', '/fuzz-500.php?c=1', '', 0, 0, 0, 1, 'human', '', 0),"
                  "(2, 1, 1, '6666cd76f96956469e7be39d750cc7d8', '/maxsize', '', 0, 0, 0, 1, 'human', '', 0)")

        assert self.db.fetch_one("SELECT COUNT(id) FROM requests") == 0
        out = self._run('normal', [
            './main.py', 'test', 'FuzzerHeaders', 'scan', '--host=wrtest.com', '--threads=3', '--protocol=' + protocol
        ])
        assert out.count('but limit in config')
        assert self.db.fetch_one("SELECT COUNT(id) FROM requests") == 2
        assert self.db.fetch_one("SELECT COUNT(id) FROM requests WHERE `path`='/fuzz-h.php'") == 1
        assert self.db.fetch_one("SELECT COUNT(id) FROM requests WHERE `path`='/fuzz-500.php'") == 1
        assert self.db.fetch_one("SELECT headers FROM requests  WHERE `path`='/fuzz-h.php'").count('X-Client-Ip') == 1
        assert self.db.fetch_one(
            "SELECT headers FROM requests  WHERE `path`='/fuzz-500.php'").count('X-Forwarded-For') == 1

    def test_scan_head(self):
        self._prepare_db()
        self.db.q("INSERT INTO `urls`"
                  "(id, project_id, host_id, hash, url, referer, response_code, response_time, "
                  "size, when_add, who_add, descr, spidered)"
                  "VALUES (1, 1, 1, '6666cd76f96956469e7be39d750cc7d9', "
                  "'/fuzz-h.php?a=1&b=2', '', 0, 0, 0, 1, 'human', '', 0),"
                  "(2, 1, 1, '6666cd76f96956469e7be39d750cc7d8', '/maxsize', '', 0, 0, 0, 1, 'human', '', 0)")

        assert self.db.fetch_one("SELECT COUNT(id) FROM requests") == 0
        out = self._run('normal', [
            './main.py', 'test', 'FuzzerHeaders', 'scan', '--host=wrtest.com', '--threads=3', '--method=HEAD'
        ])
        assert out.count('but limit in config')

    error_cmds = [
        (
            [
                './main.py', 'test', 'FuzzerHeaders', 'scan', '--host=wrtest.com', '--threads=3', '--method=test'
            ],
            'Method param must be only '
        ),
        (
            [
                './main.py', 'test', 'FuzzerHeaders', 'scan', '--host=wrtest.com', '--threads=3', '--protocol=test'
            ],
            'Protocol param must be '
        ),
        (
            [
                './main.py', 'test', 'FuzzerHeaders', 'scan', '--host=notfound.com', '--threads=3'
            ],
            'not found in this project'
        )
    ]
    @pytest.mark.parametrize("cmd_set,check_phrase", error_cmds)
    def test_error(self, cmd_set, check_phrase):
        self._prepare_db()
        out = self._run('normal', cmd_set)
        assert out.count(check_phrase)
