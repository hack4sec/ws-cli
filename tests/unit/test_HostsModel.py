# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Unit tests for HostsModel
"""

import sys
import os

wrpath = os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + '/../../')
testpath = os.path.realpath(os.path.dirname(os.path.realpath(__file__)))

sys.path.append(wrpath)
sys.path.append(wrpath + '/classes/models')

from Common import Common
from classes.models.HostsModel import HostsModel


class Test_HostsModel(Common):
    """Unit tests for HostsModel"""
    model = None

    def setup(self):
        self.model = HostsModel()
        self.db.q("TRUNCATE TABLE `hosts`")
        self.db.q("TRUNCATE TABLE `ips`")

    def test_get_id_by_name(self):
        self.db.q("INSERT INTO `hosts` (id, project_id, ip_id, name, descr) VALUES (2,1,1,'test.com', '')")
        assert self.model.get_id_by_name(1, 'test.com') == 2

    def test_exists(self):
        self.db.q("INSERT INTO `hosts` (id, project_id, ip_id, name, descr) VALUES (2,1,1,'test.com', '')")
        assert self.model.exists(1, 'test.com')
        assert not self.model.exists(1, 'test1.com')

    def test_add(self):
        assert not self.model.exists(1, 'test.com')
        assert self.model.add(1, 1, 'test.com', '') == 1
        assert self.model.exists(1, 'test.com')

    def test_list(self):
        self.db.q("INSERT INTO `ips` (id, project_id, ip, descr) VALUES (1, 1, '111.111.111.111', '')")

        self.db.q("INSERT INTO `hosts` (id, project_id, ip_id, name, descr) VALUES (1, 1, 1, 'test1.com', 'desc1')")
        self.db.q("INSERT INTO `hosts` (id, project_id, ip_id, name, descr) VALUES (2, 1, 1, 'test2.com', 'desc2')")
        self.db.q("INSERT INTO `hosts` (id, project_id, ip_id, name, descr) VALUES (3, 1, 1, 'test3.com', 'desc3')")

        test_data = [
            {'id': 1, 'name': 'test1.com', 'ip': '111.111.111.111', 'descr': 'desc1'},
            {'id': 2, 'name': 'test2.com', 'ip': '111.111.111.111', 'descr': 'desc2'},
            {'id': 3, 'name': 'test3.com', 'ip': '111.111.111.111', 'descr': 'desc3'},
        ]

        assert test_data == self.model.list(1, '111.111.111.111')

    def test_list_of_names(self):
        self.db.q("INSERT INTO `ips` (id, project_id, ip, descr) VALUES (1, 1, '111.111.111.111', '')")

        self.db.q("INSERT INTO `hosts` (id, project_id, ip_id, name, descr) VALUES (1, 1, 1, 'test1.com', 'desc1')")
        self.db.q("INSERT INTO `hosts` (id, project_id, ip_id, name, descr) VALUES (2, 1, 1, 'test2.com', 'desc2')")
        self.db.q("INSERT INTO `hosts` (id, project_id, ip_id, name, descr) VALUES (3, 1, 1, 'test3.com', 'desc3')")

        test_data = ['test1.com', 'test2.com', 'test3.com']

        assert test_data == self.model.list_of_names(1)

    def test_delete(self):
        self.db.q("INSERT INTO `hosts` (id, project_id, ip_id, name, descr) VALUES (2,1,1,'test.com', '')")
        assert self.model.exists(1, 'test.com')
        self.model.delete(1, 'test.com')
        assert not self.model.exists(1, 'test.com')
