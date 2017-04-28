#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os

wrpath   = os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + '/../../')
testpath = os.path.realpath(os.path.dirname(os.path.realpath(__file__)))

sys.path.append(wrpath + '/classes/models')

from ModelsCommon import ModelsCommon
from classes.models.HostsInfoModel import HostsInfoModel

class Test_HostsInfoModel(ModelsCommon):
    model = None

    def setup(self):
        self.db.q("TRUNCATE TABLE `hosts_info`")
        self.model = HostsInfoModel()

    def teardown(self):
        del self.model

    # Проверка добавления и замены информации о хосте
    def test_replace(self):
        assert self.db.fetch_one("SELECT COUNT(*) FROM hosts_info") == 0
        self.model.set_info(1, 1, 'test_key', 'test_value1')
        assert self.db.fetch_one("SELECT COUNT(*) FROM hosts_info WHERE `value`='test_value1' AND `key`='test_key'") == 1
        self.model.set_info(1, 1, 'test_key', 'test_value2')
        assert self.db.fetch_one("SELECT COUNT(*) FROM hosts_info WHERE `value`='test_value2' AND `key`='test_key'") == 1
        assert self.db.fetch_one("SELECT COUNT(*) FROM hosts_info") == 1