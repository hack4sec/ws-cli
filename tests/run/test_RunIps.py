# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Tests of Ips module
"""
import sys
import os
import subprocess

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
from libs.common import *


class Test_RunIps(CommonTest):
    """Tests of Ips module"""
    def test_add(self):
        assert self.db.fetch_one("SELECT COUNT(id) FROM ips") == 0
        self.db.q("INSERT INTO projects (id, name, descr) VALUES(1, 'test', 'desc1')")

        self._replace_config('normal')
        os.chdir(wrpath)
        out = subprocess.check_output([
            './main.py', 'test', 'IPs', 'add', '--ip', '127.0.0.1'
        ])
        self._restore_config()
        self.output_errors(out)

        assert bool(out.find("successfully added") > -1)
        assert self.db.fetch_one("SELECT COUNT(id) FROM ips") == 1
        
    def test_add_exists(self):
        self.db.q("INSERT INTO projects (id, name, descr) VALUES(1, 'test', 'desc1')")
        self.db.q("INSERT INTO ips (id, project_id, ip, descr) VALUES(1, 1, '127.0.0.1', '')")

        self._replace_config('normal')
        os.chdir(wrpath)
        out = subprocess.check_output([
            './main.py', 'test', 'IPs', 'add', '--ip', '127.0.0.1'
        ])
        self._restore_config()
        self.output_errors(out)

        assert bool(out.find("successfully added") == -1)
        assert bool(out.find("already exists") > -1)
        assert self.db.fetch_one("SELECT COUNT(id) FROM ips") == 1

    def test_add_invalid_ip(self):
        self.db.q("INSERT INTO projects (id, name, descr) VALUES(1, 'test', 'desc1')")

        self._replace_config('normal')
        os.chdir(wrpath)
        out = subprocess.check_output([
            './main.py', 'test', 'IPs', 'add', '--ip', '127.0.0.a'
        ])
        self._restore_config()
        self.output_errors(out)

        assert bool(out.find("successfully added") == -1)
        assert bool(out.find("is not valid ip-address") > -1)
        assert self.db.fetch_one("SELECT COUNT(id) FROM ips") == 0

    def test_list(self):
        self.db.q("INSERT INTO projects (id, name, descr) VALUES(1, 'test', 'desc1')")
        self.db.q("INSERT INTO ips (id, project_id, ip, descr) VALUES(1, 1, '127.0.0.1', 'ipdesc1')")
        self.db.q("INSERT INTO ips (id, project_id, ip, descr) VALUES(2, 1, '127.0.0.2', 'ipdesc2')")
        self.db.q("INSERT INTO ips (id, project_id, ip, descr) VALUES(3, 1, '127.0.0.3', 'ipdesc3')")

        self._replace_config('normal')
        os.chdir(wrpath)
        out = subprocess.check_output([
            './main.py', 'test', 'IPs', 'list'
        ])
        self._restore_config()
        self.output_errors(out)

        assert bool(out.find("127.0.0.1") > -1)
        assert bool(out.find("127.0.0.2") > -1)
        assert bool(out.find("127.0.0.3") > -1)

        assert bool(out.find("ipdesc1") > -1)
        assert bool(out.find("ipdesc2") > -1)
        assert bool(out.find("ipdesc3") > -1)

    def test_delete_invalid_ip(self):
        self.db.q("INSERT INTO projects (id, name, descr) VALUES(1, 'test', 'desc1')")

        self._replace_config('normal')
        os.chdir(wrpath)
        out = subprocess.check_output([
            './main.py', 'test', 'IPs', 'delete', '--ip', '127.0.0.a'
        ])
        self._restore_config()
        self.output_errors(out)

        assert bool(out.find("is not valid ip-address") > -1)

    def test_delete_not_exists(self):
        self.db.q("INSERT INTO projects (id, name, descr) VALUES(1, 'test', 'desc1')")

        self._replace_config('normal')
        os.chdir(wrpath)
        out = subprocess.check_output([
            './main.py', 'test', 'IPs', 'delete', '--ip', '127.0.0.1'
        ])
        self._restore_config()
        self.output_errors(out)

        assert bool(out.find(" not exists in this project") > -1)

    def test_delete(self):
        self.db.q("INSERT INTO projects (id, name, descr) VALUES(1, 'test', '')")
        self.db.q("INSERT INTO ips (id, project_id, ip, descr) VALUES(1, 1, '127.0.0.1', '')")

        assert self.db.fetch_one("SELECT COUNT(id) FROM ips") == 1

        self._replace_config('normal')
        os.chdir(wrpath)
        proc = subprocess.Popen([
            './main.py', 'test', 'IPs', 'delete', '--ip', '127.0.0.1'
        ], stdin=subprocess.PIPE, stdout=open('/tmp/unittests-output', 'w'))
        proc.communicate('y\n')
        self._restore_config()
        self.output_errors(file_get_contents('/tmp/unittests-output'))

        assert self.db.fetch_one("SELECT COUNT(id) FROM ips") == 0
