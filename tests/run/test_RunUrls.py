# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Tests of Urls module
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


class Test_RunUrls(CommonTest):
    """Tests of Urls module"""
    def setup(self):
        CommonTest.setup(self)

        self.db.q("INSERT INTO projects (id, name, descr) VALUES(1, 'test', '')")
        self.db.q("INSERT INTO ips (id, project_id, ip, descr) VALUES(1, 1, '127.0.0.1', '')")
        self.db.q("INSERT INTO `hosts` (id, project_id, ip_id, name, descr) VALUES (1,1,1,'wrtest.com', 'hd1')")

    def test_list(self):
        self.db.q("INSERT INTO `urls`"
                  "(id, project_id, host_id, hash, url, referer, response_code, response_time, "
                  "size, when_add, who_add, descr, spidered)"
                  "VALUES(1, 1, 1, MD5('/one'), '/one', '', 0, 0, 0, 1, 'human', '', 0)")
        self.db.q("INSERT INTO `urls`"
                  "(id, project_id, host_id, hash, url, referer, response_code, response_time, "
                  "size, when_add, who_add, descr, spidered)"
                  "VALUES(2, 1, 1, MD5('/two'), '/two', '', 0, 0, 0, 1, 'human', '', 0)")
        self.db.q("INSERT INTO `urls`"
                  "(id, project_id, host_id, hash, url, referer, response_code, response_time, "
                  "size, when_add, who_add, descr, spidered)"
                  "VALUES(3, 1, 1, MD5('/three'), '/three', '', 0, 0, 0, 1, 'human', '', 0)")

        self._replace_config('normal')
        os.chdir(wrpath)
        out = subprocess.check_output([
            './main.py', 'test', 'Urls', 'list', '--host=wrtest.com'
        ])
        self._restore_config()
        self.output_errors(out)

        assert out.find("/one") > -1
        assert out.find("/two") > -1
        assert out.find("/three") > -1

    def test_export(self):
        self.db.q("INSERT INTO `urls`"
                  "(id, project_id, host_id, hash, url, referer, response_code, response_time, "
                  "size, when_add, who_add, descr, spidered)"
                  "VALUES(1, 1, 1, MD5('/one'), '/one', '', 0, 0, 0, 1, 'human', '', 0)")
        self.db.q("INSERT INTO `urls`"
                  "(id, project_id, host_id, hash, url, referer, response_code, response_time, "
                  "size, when_add, who_add, descr, spidered)"
                  "VALUES(2, 1, 1, MD5('/two'), '/two', '', 0, 0, 0, 1, 'human', '', 0)")
        self.db.q("INSERT INTO `urls`"
                  "(id, project_id, host_id, hash, url, referer, response_code, response_time, "
                  "size, when_add, who_add, descr, spidered)"
                  "VALUES(3, 1, 1, MD5('/three'), '/three', '', 0, 0, 0, 1, 'human', '', 0)")

        self._replace_config('normal')
        os.chdir(wrpath)
        out = subprocess.check_output([
            './main.py', 'test', 'Urls', 'export', '--host=wrtest.com'
        ])
        self._restore_config()
        self.output_errors(out)

        assert out.find("http://wrtest.com/one") > -1
        assert out.find("http://wrtest.com/two") > -1
        assert out.find("http://wrtest.com/three") > -1

    def test_list_like(self):
        self.db.q("INSERT INTO `urls`"
                  "(id, project_id, host_id, hash, url, referer, response_code, response_time, "
                  "size, when_add, who_add, descr, spidered)"
                  "VALUES(1, 1, 1, MD5('/one'), '/one', '', 0, 0, 0, 1, 'human', '', 0)")
        self.db.q("INSERT INTO `urls`"
                  "(id, project_id, host_id, hash, url, referer, response_code, response_time, "
                  "size, when_add, who_add, descr, spidered)"
                  "VALUES(2, 1, 1, MD5('/two'), '/two', '', 0, 0, 0, 1, 'human', '', 0)")
        self.db.q("INSERT INTO `urls`"
                  "(id, project_id, host_id, hash, url, referer, response_code, response_time, "
                  "size, when_add, who_add, descr, spidered)"
                  "VALUES(3, 1, 1, MD5('/three'), '/three', '', 0, 0, 0, 1, 'human', '', 0)")

        self._replace_config('normal')
        os.chdir(wrpath)
        out = subprocess.check_output([
            './main.py', 'test', 'Urls', 'list', '--host=wrtest.com', '--like=t'
        ])
        self._restore_config()
        self.output_errors(out)

        assert out.find("/one") == -1
        assert out.find("/two") > -1
        assert out.find("/three") > -1

    def test_add(self):
        assert self.db.fetch_one("SELECT COUNT(id) FROM urls") == 0

        self._replace_config('normal')
        os.chdir(wrpath)
        out = subprocess.check_output([
            './main.py', 'test', 'Urls', 'add', '--host=wrtest.com', '--url=/'
        ])
        self._restore_config()
        self.output_errors(out)

        assert out.find("successfully added") > -1
        assert self.db.fetch_one("SELECT COUNT(id) FROM urls") == 1

    def test_add_exists(self):
        self.db.q("INSERT INTO `urls`"
                  "(id, project_id, host_id, hash, url, referer, response_code, response_time, "
                  "size, when_add, who_add, descr, spidered)"
                  "VALUES(1, 1, 1, MD5('/'), '/', '', 0, 0, 0, 1, 'human', '', 0)")

        assert self.db.fetch_one("SELECT COUNT(id) FROM urls") == 1

        self._replace_config('normal')
        os.chdir(wrpath)
        out = subprocess.check_output([
            './main.py', 'test', 'Urls', 'add', '--host=wrtest.com', '--url=/'
        ])
        self._restore_config()
        self.output_errors(out)

        assert out.find("already exists ") > -1
        assert self.db.fetch_one("SELECT COUNT(id) FROM urls") == 1

    def test_add_url_error_url(self):
        assert self.db.fetch_one("SELECT COUNT(id) FROM urls") == 0

        self._replace_config('normal')
        os.chdir(wrpath)
        out = subprocess.check_output([
            './main.py', 'test', 'Urls', 'add', '--host=wrtest.com', '--url=aaa'
        ])
        self._restore_config()
        self.output_errors(out)

        assert out.find("URL must start from") > -1
        assert self.db.fetch_one("SELECT COUNT(id) FROM urls") == 0

    def test_add_url_error_host(self):
        assert self.db.fetch_one("SELECT COUNT(id) FROM urls") == 0

        self._replace_config('normal')
        os.chdir(wrpath)
        out = subprocess.check_output([
            './main.py', 'test', 'Urls', 'add', '--host=wrtest2.com', '--url=/'
        ])
        self._restore_config()
        self.output_errors(out)

        assert out.find("not found in this") > -1
        assert self.db.fetch_one("SELECT COUNT(id) FROM urls") == 0

    def test_delete_not_exists(self):
        self._replace_config('normal')
        os.chdir(wrpath)
        out = subprocess.check_output([
            './main.py', 'test', 'Urls', 'delete', '--host=wrtest.com', '--url=/aaa'
        ])
        self._restore_config()
        self.output_errors(out)

        assert out.find("not exists in this project") > -1

    def test_delete(self):
        self.db.q("INSERT INTO `urls`"
                  "(id, project_id, host_id, hash, url, referer, response_code, response_time, "
                  "size, when_add, who_add, descr, spidered)"
                  "VALUES(1, 1, 1, MD5('/'), '/', '', 0, 0, 0, 1, 'human', '', 0)")

        assert self.db.fetch_one("SELECT COUNT(id) FROM urls") == 1

        self._replace_config('normal')
        os.chdir(wrpath)
        proc = subprocess.Popen([
            './main.py', 'test', 'Urls', 'delete', '--host=wrtest.com', '--url=/'
        ], stdin=subprocess.PIPE, stdout=open('/tmp/unittests-output', 'w'))
        proc.communicate('y\n')
        self._restore_config()
        self.output_errors(file_get_contents('/tmp/unittests-output'))

        assert self.db.fetch_one("SELECT COUNT(id) FROM urls") == 0
