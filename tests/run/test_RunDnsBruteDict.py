# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Tests of DnsBruteDict module
"""
import sys
import os
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

from CommonDnsBruteTest import CommonDnsBruteTest

class Test_RunDnsBruteDict(CommonDnsBruteTest):
    """Tests of DnsBruteDict module"""
    def test_brute(self):
        self._prepare_db()
        out = self._run(
            'normal',
            [
                './main.py', 'test', 'DnsBruteDict', 'brute', '--host=wrtest.com',
                '--dict=tests/run/files/dns.txt', '--template=@'
            ]
        )

        assert self.db.fetch_one("SELECT COUNT(id) FROM hosts") == 3
        assert out.find("aaa.wrtest.com") != -1
        assert out.find("www.wrtest.com") != -1
        assert "127.0.0.1" in out

    def test_brute_diff_msymbol(self):
        self._prepare_db()
        out = self._run(
            'normal',
            [
                './main.py', 'test', 'DnsBruteDict', 'brute', '--host=wrtest.com',
                '--dict=tests/run/files/dns.txt', '--msymbol=%', '--template=%'
            ]
        )

        assert self.db.fetch_one("SELECT COUNT(id) FROM hosts") == 3
        assert out.find("aaa.wrtest.com") != -1
        assert out.find("www.wrtest.com") != -1
        assert "127.0.0.1" in out

    protocols_data = [
        ('tcp'),
        ('udp')
    ]
    @pytest.mark.parametrize("protocol", protocols_data)
    def test_proto(self, protocol):
        self._prepare_db()
        out = self._run(
            'normal',
            [
                './main.py', 'test', 'DnsBruteDict', 'brute', '--host=wrtest.com',
                '--dict=tests/run/files/dns.txt', '--protocol=' + protocol, '--template=@'
            ]
        )

        assert self.db.fetch_one("SELECT COUNT(id) FROM hosts") == 3
        assert out.find("aaa.wrtest.com") != -1
        assert out.find("www.wrtest.com") != -1
        assert "127.0.0.1" in out

    errors_data = [
        (
            [
                './main.py', 'test', 'DnsBruteDict', 'brute', '--host=wrtest.com',
                '--dict=false.txt', '--protocol=udp', '--template=@'
            ],
            'not exists or not readable'
        ),
        (
            [
                './main.py', 'test', 'DnsBruteDict', 'brute', '--host=wrtest.com',
                '--dict=tests/run/files/dns.txt', '--protocol=test', '--template=@'
            ],
            "Protocol mast be 'tcp', 'udp' or 'auto'"
        ),
    ]
    @pytest.mark.parametrize("cmd_set,check_error", errors_data)
    def test_errors(self, cmd_set, check_error):
        self._prepare_db()
        out = self._run(
            'normal',
            cmd_set
        )
        assert out.count(check_error)
