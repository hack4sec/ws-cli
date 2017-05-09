# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Tests of Projects module
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


class Test_RunProjects(CommonTest):
    """Tests of Projects module"""
    def test_list(self):
        self.db.q("INSERT INTO projects (id, name, descr) VALUES(1, 'prj1', 'desc1')")
        self.db.q("INSERT INTO projects (id, name, descr) VALUES(2, 'prj2', 'desc2')")
        self.db.q("INSERT INTO projects (id, name, descr) VALUES(3, 'prj3', 'desc3')")

        self._replace_config('normal')
        os.chdir(wrpath)
        out = subprocess.check_output([
            './main.py', 'test', 'Projects', 'list'
        ])
        self._restore_config()
        self.output_errors(out)

        assert out.find("prj1") > -1
        assert out.find("prj2") > -1
        assert out.find("prj3") > -1
        assert out.find("desc1") > -1
        assert out.find("desc2") > -1
        assert out.find("desc3") > -1

    def test_create(self):
        assert self.db.fetch_one("SELECT COUNT(id) FROM projects") == 0

        self._replace_config('normal')
        os.chdir(wrpath)
        out = subprocess.check_output([
            './main.py', 'test', 'Projects', 'add'
        ])
        self._restore_config()
        self.output_errors(out)

        assert out.find("successfully created") > -1
        assert self.db.fetch_one("SELECT id FROM projects WHERE name='test'") == 1

    def test_create_exists(self):
        self.db.q("INSERT INTO projects (id, name, descr) VALUES(1, 'test', 'desc1')")

        self._replace_config('normal')
        os.chdir(wrpath)
        out = subprocess.check_output([
            './main.py', 'test', 'Projects', 'add'
        ])
        self._restore_config()
        self.output_errors(out)

        assert out.find("successfully created") == -1
        assert out.find("already exists") > -1

        assert self.db.fetch_one("SELECT COUNT(id) FROM projects") == 1

    def test_delete(self):
        self.db.q("INSERT INTO projects (id, name, descr) VALUES(1, 'test', 'desc1')")

        assert self.db.fetch_one("SELECT COUNT(id) FROM projects") == 1

        self._replace_config('normal')
        os.chdir(wrpath)
        proc = subprocess.Popen([
            './main.py', 'test', 'Projects', 'delete'
        ], stdin=subprocess.PIPE, stdout=open('/tmp/unittests-output', 'w'))
        proc.communicate('y\n')
        self._restore_config()
        self.output_errors(file_get_contents('/tmp/unittests-output'))

        assert self.db.fetch_one("SELECT COUNT(id) FROM projects") == 0

    def test_delete_not_exists(self):
        self._replace_config('normal')
        os.chdir(wrpath)
        out = subprocess.check_output([
            './main.py', 'test1', 'Projects', 'delete'
        ])
        self._restore_config()
        self.output_errors(out)

        assert out.find("not exists") > -1
