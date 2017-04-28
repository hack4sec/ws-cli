#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, unittest

wrpath   = os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + '/../')
testpath = os.path.realpath(os.path.dirname(os.path.realpath(__file__)))

sys.path.append(wrpath)
sys.path.append(wrpath + '/classes/models')

from ModelsCommon import ModelsCommon
from classes.models.HostsModel import HostsModel


class Test_HostsModel(ModelsCommon):
    model = None

    def setup(self):
        self.model = HostsModel()
        self.db.q("TRUNCATE TABLE `hosts`")
        self.db.q("TRUNCATE TABLE `ips`")

    # Проверка выборки хоста по имени
    def test_get_id_by_name(self):
        self.db.q("INSERT INTO `hosts` (id, project_id, ip_id, name, descr) VALUES (2,1,1,'test.com', '')")
        assert self.model.get_id_by_name(1, 'test.com') == 2

    # Проверка существования хоста
    def test_exists(self):
        self.db.q("INSERT INTO `hosts` (id, project_id, ip_id, name, descr) VALUES (2,1,1,'test.com', '')")
        assert self.model.exists(1, 'test.com')
        assert not self.model.exists(1, 'test1.com')

    # Проверка добавления хоста
    def test_add(self):
        assert not self.model.exists(1, 'test.com')
        id = self.model.add(1, 1, 'test.com', '')
        assert id == 1
        assert self.model.exists(1, 'test.com')

    # Проверка вывода списка хостов
    def test_list(self):
        self.db.q("INSERT INTO `ips` (id, project_id, ip, descr) VALUES (1, 1, '111.111.111.111', '')")

        self.db.q("INSERT INTO `hosts` (id, project_id, ip_id, name, descr) VALUES (1, 1, 1, 'test1.com', 'desc1')")
        self.db.q("INSERT INTO `hosts` (id, project_id, ip_id, name, descr) VALUES (2, 1, 1, 'test2.com', 'desc2')")
        self.db.q("INSERT INTO `hosts` (id, project_id, ip_id, name, descr) VALUES (3, 1, 1, 'test3.com', 'desc3')")

        test_data = [
                { 'id': 1, 'name': 'test1.com', 'ip': '111.111.111.111', 'descr': 'desc1' },
                { 'id': 2, 'name': 'test2.com', 'ip': '111.111.111.111', 'descr': 'desc2' },
                { 'id': 3, 'name': 'test3.com', 'ip': '111.111.111.111', 'descr': 'desc3' },
        ]

        assert test_data == self.model.list(1, '111.111.111.111')

    # Проверка удаления хоста
    def test_delete(self):
        self.db.q("INSERT INTO `hosts` (id, project_id, ip_id, name, descr) VALUES (2,1,1,'test.com', '')")
        assert self.model.exists(1, 'test.com')
        self.model.delete(1, 'test.com')
        assert not self.model.exists(1, 'test.com')
