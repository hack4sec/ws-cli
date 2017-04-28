#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, unittest

wrpath   = os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + '/../')
testpath = os.path.realpath(os.path.dirname(os.path.realpath(__file__)))

sys.path.append(wrpath + '/classes')
sys.path.append(wrpath + '/classes/models')

from ModelsCommon import ModelsCommon
from classes.models.IpsModel import IpsModel


class Test_IpsModel(ModelsCommon):
    model = None

    def setup(self):
        self.model = IpsModel()
        self.db.q("TRUNCATE TABLE ips")

    # Проверка выборки или добавления в случае отсутствия записи (IP существует)
    def test_get_id_or_add_get(self):
        self.db.q("INSERT INTO ips (id, project_id, ip, descr) VALUES(2, 1, '111.111.111.111', '')")

        start_count = self.db.fetch_one("SELECT COUNT(id) FROM ips")
        assert start_count == 1

        assert self.model.get_id_or_add(1, '111.111.111.111') == 2

        assert start_count == self.db.fetch_one("SELECT COUNT(id) FROM ips")
    # Проверка выборки или добавления в случае отсутствия записи (IP не существует)
    def test_get_id_or_add_add(self):
        start_count = self.db.fetch_one("SELECT COUNT(id) FROM ips")
        assert start_count == 0

        assert self.model.get_id_or_add(1, '111.111.111.111') == 1

        assert start_count == self.db.fetch_one("SELECT COUNT(id) FROM ips")-1

    # Проверка существования IP
    def test_exists(self):
        self.db.q("INSERT INTO ips (id, project_id, ip, descr) VALUES(2, 1, '111.111.111.111', '')")
        assert self.model.exists(1, '111.111.111.111')
        assert not self.model.exists(1, '1.1.1.1')

    # Проверка добавления IP
    def test_add(self):
        assert not self.model.exists(1, '1.1.1.1')
        id = self.model.add(1, '1.1.1.1', '')
        assert id == 1
        assert self.model.exists(1, '1.1.1.1')

    # Проверка вывода списка IP
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

    # Проверка удаления IP
    def test_delete(self):
        self.db.q("INSERT INTO ips (id, project_id, ip, descr) VALUES(1, 1, '1.1.1.1', '')")
        assert self.model.exists(1, '1.1.1.1')
        self.model.delete(1, '1.1.1.1')
        assert not self.model.exists(1, '1.1.1.1')
