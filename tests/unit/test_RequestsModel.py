#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os

wrpath   = os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + '/../../')
testpath = os.path.realpath(os.path.dirname(os.path.realpath(__file__)))

sys.path.append(wrpath + '/classes')
sys.path.append(wrpath + '/classes/models')

from ModelsCommon import ModelsCommon
from classes.models.RequestsModel import RequestsModel

class Test_RequestsModel(ModelsCommon):
    model = None

    def setup(self):
        self.model = RequestsModel()
        self.db.q("TRUNCATE TABLE `requests`")

    # Добавление нового запроса
    def test_add(self):
        assert self.db.fetch_one("SELECT COUNT(id) FROM requests") == 0
        self.model.add(1, 1, '/index.php', 'a=b', {}, 'get', 'http', 'human', 'some comment')
        assert self.db.fetch_one("SELECT COUNT(id) FROM requests") == 1

    # Добавление существующего запроса
    def test_add_exists(self):
        self.db.q(
            "INSERT INTO `requests` "
            "(`id`, `hash`, `project_id`, `host_id`, `path`, `params`, `method`, `protocol`, `founder`, `comment`)"
            " VALUES "
            "(1, 'bb05bd33eea8c0f0bbf0cd7ea8ddbaf4', 1, 1, '/index.php', 'a=b', 'get', 'http', 'human', 'some comment')"
            "");
        assert self.db.fetch_one("SELECT COUNT(id) FROM requests") == 1
        self.model.add(1, 1, '/index.php', 'a=b', {}, 'get', 'http', 'human', 'some comment')
        assert self.db.fetch_one("SELECT COUNT(id) FROM requests") == 1
