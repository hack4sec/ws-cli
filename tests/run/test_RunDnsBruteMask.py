# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Tests of DnsBruteMask module
"""

import sys
import os

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

class Test_RunDnsBruteMask(CommonDnsBruteTest):
    """Tests of DnsBruteMask module"""

    def test_brute_mask_wo_len(self):
        self._prepare_db()
        self._run(
            'normal',
            [
                './main.py', 'test', 'DnsBruteMask', 'brute',
                '--host=wrtest.com', '--mask=?l?l', '--threads=3', '--template=@'
            ]
        )

        assert self.db.fetch_one("SELECT COUNT(id) FROM hosts") == 3

    def test_brute_mask_w_len(self):
        self._prepare_db()
        out = self._run(
            'normal',
            [
                './main.py', 'test', 'DnsBruteMask', 'brute', '--host=wrtest.com',
                '--mask=?l,1,2', '--threads=3', '--template=@'
            ]
        )

        assert out.find("dd.wrtest.com") != -1
        assert out.find("zz.wrtest.com") != -1
        assert out.find("b.wrtest.com") != -1
        assert out.find("k.wrtest.com") != -1
        assert out.find("y.wrtest.com") != -1
        assert "127.0.0.1" in out

        assert self.db.fetch_one("SELECT COUNT(id) FROM hosts") == 6
