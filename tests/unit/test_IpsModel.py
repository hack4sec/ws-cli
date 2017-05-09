# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Unit tests for IpsModel
"""

import sys
import os

wrpath = os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + '/../../')
testpath = os.path.realpath(os.path.dirname(os.path.realpath(__file__)))

sys.path.append(wrpath + '/classes')
sys.path.append(wrpath + '/classes/models')

from Common import Common
from classes.models.IpsModel import IpsModel


class Test_IpsModel(Common):
    """Unit tests for IpsModel"""
    model = None

    def setup(self):
        self.model = IpsModel()
        self.db.q("TRUNCATE TABLE ips")

    def test_get_id_or_add_get(self):
        self.db.q("INSERT INTO ips (id, project_id, ip, descr) VALUES(2, 1, '111.111.111.111', '')")

        start_count = self.db.fetch_one("SELECT COUNT(id) FROM ips")
        assert start_count == 1

        assert self.model.get_id_or_add(1, '111.111.111.111') == 2

        assert start_count == self.db.fetch_one("SELECT COUNT(id) FROM ips")

    def test_get_id_or_add_add(self):
        start_count = self.db.fetch_one("SELECT COUNT(id) FROM ips")
        assert start_count == 0

        assert self.model.get_id_or_add(1, '111.111.111.111') == 1

        assert start_count == self.db.fetch_one("SELECT COUNT(id) FROM ips")-1

    def test_exists(self):
        self.db.q("INSERT INTO ips (id, project_id, ip, descr) VALUES(2, 1, '111.111.111.111', '')")
        assert self.model.exists(1, '111.111.111.111')
        assert not self.model.exists(1, '1.1.1.1')

    def test_add(self):
        assert not self.model.exists(1, '1.1.1.1')
        _id = self.model.add(1, '1.1.1.1', '')
        assert _id == 1
        assert self.model.exists(1, '1.1.1.1')

    def test_list(self):
        self.db.q("INSERT INTO ips (id, project_id, ip, descr) VALUES(1, 1, '1.1.1.1', '')")
        self.db.q("INSERT INTO ips (id, project_id, ip, descr) VALUES(2, 1, '1.1.1.2', '')")
        self.db.q("INSERT INTO ips (id, project_id, ip, descr) VALUES(3, 1, '1.1.1.3', '')")

        test_data = [
            {'id': 1, 'ip': '1.1.1.1', 'descr': ''},
            {'id': 2, 'ip': '1.1.1.2', 'descr': ''},
            {'id': 3, 'ip': '1.1.1.3', 'descr': ''}
        ]

        assert test_data == self.model.list(1)

    def test_delete(self):
        self.db.q("INSERT INTO ips (id, project_id, ip, descr) VALUES(1, 1, '1.1.1.1', '')")
        assert self.model.exists(1, '1.1.1.1')
        self.model.delete(1, '1.1.1.1')
        assert not self.model.exists(1, '1.1.1.1')
