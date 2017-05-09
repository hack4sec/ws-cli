# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Tests of Main module
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


class Test_RunMain(CommonTest):
    """Tests of Main module"""
    def test_run_usage(self):
        self._replace_config('normal')
        os.chdir(wrpath)
        out = subprocess.check_output([
            './main.py'
        ])
        self._restore_config()
        self.output_errors(out)
        assert bool(out.count("Usage"))

    def test_run_error_module_not_exists(self):
        self._replace_config('normal')
        os.chdir(wrpath)
        out = subprocess.check_output([
            './main.py', 'test', 'Proj', "aaaaaa"
        ])
        self._restore_config()
        self.output_errors(out)
        assert bool(out.count("ERROR: Module") and out.count("not exists"))

    def test_run_action_not_exists(self):
        self._replace_config('normal')
        os.chdir(wrpath)
        out = subprocess.check_output([
            './main.py', 'test', 'Projects', "aaaaaa"
        ])
        self._restore_config()
        self.output_errors(out)
        assert bool(out.count("ERROR: Action") and out.count("not exists"))

    def test_run_project_help(self):
        self._replace_config('normal')
        os.chdir(wrpath)
        out = subprocess.check_output([
            './main.py', 'test', 'Projects', "list", "-h"
        ])
        self._restore_config()
        self.output_errors(out)
        assert bool(out.count("sage"))


    def test_run_fail_param(self):
        self._replace_config('normal')
        os.chdir(wrpath)
        try:
            subprocess.check_output([
                './main.py', 'test', 'Projects', "list", "--kol"
            ], stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            assert bool(str(e).count("returned non-zero exit status 2"))
        self._restore_config()

    def test_run_not_host(self):
        self._replace_config('normal')
        os.chdir(wrpath)
        try:
            subprocess.check_output([
                './main.py', 'test', 'Urls', "list",
            ], stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            assert bool(str(e).count("returned non-zero exit status 2"))
        self._restore_config()
