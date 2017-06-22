# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Tests of Hosts module
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
from libs.common import file_get_contents


class Test_RunHosts(CommonTest):
    """Tests of Hosts module"""
    def test_add(self):
        self.db.q("INSERT INTO projects (id, name, descr) VALUES(1, 'test', 'desc1')")
        self.db.q("INSERT INTO ips (id, project_id, ip, descr) VALUES(1, 1, '127.0.0.1', 'ipdesc1')")

        assert self.db.fetch_one("SELECT COUNT(id) FROM hosts") == 0

        self._replace_config('normal')
        os.chdir(wrpath)
        out = subprocess.check_output([
            './main.py', 'test', 'Hosts', 'add', '--host=wrtest.com', '--ip=127.0.0.1'
        ])
        self._restore_config()
        self.output_errors(out)

        assert out.find("Host 'wrtest.com' successfully added to project 'test' with IP '127.0.0.1'") > -1
        assert self.db.fetch_one("SELECT COUNT(id) FROM hosts") == 1

    def test_add_list(self):
        self.db.q("INSERT INTO projects (id, name, descr) VALUES(1, 'test', 'desc1')")
        self.db.q("INSERT INTO ips (id, project_id, ip, descr) VALUES(1, 1, '127.0.0.1', 'ipdesc1')")

        assert self.db.fetch_one("SELECT COUNT(id) FROM hosts") == 0

        self._replace_config('normal')
        os.chdir(wrpath)
        out = subprocess.check_output([
            './main.py', 'test', 'Hosts', 'addlist', '--file=tests/run/files/hosts-list.txt'
        ])
        self._restore_config()
        self.output_errors(out)

        assert out.find("Host 'ya.ru' successfully added to project 'test'") > -1
        assert out.find("Host 'www.com' successfully added to project 'test'") > -1
        assert out.find("Host 'google.com' successfully added to project 'test'") > -1

        assert self.db.fetch_one("SELECT COUNT(id) FROM hosts") == 3

    def test_add_ip_lookup(self):
        self.db.q("INSERT INTO projects (id, name, descr) VALUES(1, 'test', 'desc1')")

        assert self.db.fetch_one("SELECT COUNT(id) FROM hosts") == 0

        self._replace_config('normal')
        os.chdir(wrpath)
        out = subprocess.check_output([
            './main.py', 'test', 'Hosts', 'add', '--host=wrtest.com'
        ])
        self._restore_config()
        self.output_errors(out)

        assert out.find("IP for host 'wrtest.com' is '127.0.0.1'") > -1
        assert out.find("IP '127.0.0.1' was automatically added to project ") > -1
        assert out.find("Host 'wrtest.com' successfully added to project 'test' with IP '127.0.0.1'") > -1
        assert self.db.fetch_one("SELECT COUNT(id) FROM hosts") == 1

    def test_add_bad_ip(self):
        self.db.q("INSERT INTO projects (id, name, descr) VALUES(1, 'test', 'desc1')")

        assert self.db.fetch_one("SELECT COUNT(id) FROM hosts") == 0

        self._replace_config('normal')
        os.chdir(wrpath)
        out = subprocess.check_output([
            './main.py', 'test', 'Hosts', 'add', '--host=wrtest.com', '--ip=a.a.a.a'
        ])
        self._restore_config()
        self.output_errors(out)

        assert out.find(" is not valid ip-address") > -1
        assert self.db.fetch_one("SELECT COUNT(id) FROM hosts") == 0

    def test_add_ip_lookup_error(self):
        self.db.q("INSERT INTO projects (id, name, descr) VALUES(1, 'test', 'desc1')")

        assert self.db.fetch_one("SELECT COUNT(id) FROM hosts") == 0

        self._replace_config('normal')
        os.chdir(wrpath)
        out = subprocess.check_output([
            './main.py', 'test', 'Hosts', 'add', '--host=weglleupgiwohdgowihdhgow.com'
        ])
        self._restore_config()
        self.output_errors(out)

        assert out.find("Can`t lookup hostname") > -1
        assert self.db.fetch_one("SELECT COUNT(id) FROM hosts") == 0

    def test_list(self):
        self.db.q("INSERT INTO projects (id, name, descr) VALUES(1, 'test', '')")
        self.db.q("INSERT INTO ips (id, project_id, ip, descr) VALUES(1, 1, '127.0.0.1', '')")
        self.db.q("INSERT INTO `hosts` (id, project_id, ip_id, name, descr) VALUES (1,1,1,'wrtest1.com', 'hd1')")
        self.db.q("INSERT INTO `hosts` (id, project_id, ip_id, name, descr) VALUES (2,1,1,'wrtest2.com', 'hd2')")
        self.db.q("INSERT INTO `hosts` (id, project_id, ip_id, name, descr) VALUES (3,1,1,'wrtest3.com', 'hd3')")

        self._replace_config('normal')
        os.chdir(wrpath)
        out = subprocess.check_output([
            './main.py', 'test', 'Hosts', 'list', '--ip=127.0.0.1'
        ])
        self._restore_config()
        self.output_errors(out)

        assert out.find("wrtest1.com") > -1
        assert out.find("wrtest2.com") > -1
        assert out.find("wrtest3.com") > -1
        assert out.find("hd1") > -1
        assert out.find("hd2") > -1
        assert out.find("hd3") > -1

    def test_delete(self):
        self.db.q("INSERT INTO projects (id, name, descr) VALUES(1, 'test', '')")
        self.db.q("INSERT INTO ips (id, project_id, ip, descr) VALUES(1, 1, '127.0.0.1', '')")
        self.db.q("INSERT INTO hosts (id, project_id, ip_id, name, descr) VALUES (1,1,1,'wrtest.com', 'hd1')")

        assert self.db.fetch_one("SELECT COUNT(id) FROM hosts") == 1

        self._replace_config('normal')
        os.chdir(wrpath)
        proc = subprocess.Popen([
            './main.py', 'test', 'Hosts', 'delete', '--host=wrtest.com'
        ], stdin=subprocess.PIPE, stdout=open('/tmp/unittests-output', 'w'))
        proc.communicate('y\n')
        self._restore_config()
        self.output_errors(file_get_contents('/tmp/unittests-output'))

        assert self.db.fetch_one("SELECT COUNT(id) FROM hosts") == 0

    def test_delete_not_exists(self):
        self.db.q("INSERT INTO projects (id, name, descr) VALUES(1, 'test', '')")
        self.db.q("INSERT INTO ips (id, project_id, ip, descr) VALUES(1, 1, '127.0.0.1', '')")

        self._replace_config('normal')
        os.chdir(wrpath)
        out = subprocess.check_output([
            './main.py', 'test', 'Hosts', 'delete', '--host=wrtest.com'
        ])
        self._restore_config()
        self.output_errors(out)

        assert out.find("not exists in this project") > -1
