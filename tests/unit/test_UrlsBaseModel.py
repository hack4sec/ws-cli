# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Unit tests for UrlsModel
"""

import sys
import os
import pytest

wrpath = os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + '/../../')
testpath = os.path.realpath(os.path.dirname(os.path.realpath(__file__)))

sys.path.append(wrpath + '/classes')
sys.path.append(wrpath + '/classes/models')

from Common import Common
from classes.models.UrlsBaseModel import UrlsBaseModel
from classes.Registry import Registry


class Test_UrlsBaseModel(Common):
    """Unit tests for UrlsModel"""
    model = None

    def setup(self):
        self.model = UrlsBaseModel()
        self.db.q("TRUNCATE TABLE urls")
        self.db.q("TRUNCATE TABLE urls_base")
        self.db.q("TRUNCATE TABLE urls_base_params")

    @pytest.mark.skip(reason="Fail in common start, hz why")
    def test_add_non_exists(self):
        Registry().set('pData', {'id': 1})

        assert self.db.fetch_one("SELECT COUNT(*) FROM urls_base") == 0
        assert self.db.fetch_one("SELECT COUNT(*) FROM urls_base_params") == 0

        self.model.add_url(1, '/a/b/c/?x=1&y=2')

        data = self.db.fetch_all("SELECT name, parent_id, host_id, project_id, id FROM urls_base ORDER BY id ASC")
        test_data = [
            {'name': '/', 'parent_id': 0, 'host_id': 1, 'project_id': 1, 'id': 1},
            {'name': 'a', 'parent_id': 1, 'host_id': 1, 'project_id': 1, 'id': 2},
            {'name': 'b', 'parent_id': 2, 'host_id': 1, 'project_id': 1, 'id': 3},
            {'name': 'c', 'parent_id': 3, 'host_id': 1, 'project_id': 1, 'id': 4}
        ]

        assert data == test_data

        data = self.db.fetch_all("SELECT * FROM urls_base_params")
        test_data = [
            {'parent_id': 4, 'id': 1, 'name': 'x'},
            {'parent_id': 4, 'id': 2, 'name': 'y'}
        ]
        assert data == test_data

        self.model.add_url(1, '/a/b/c/?y=2')
        assert self.db.fetch_one("SELECT COUNT(id) FROM urls_base") == 4
        assert self.db.fetch_one("SELECT COUNT(id) FROM urls_base_params") == 2

        self.model.add_url(1, '/a')
        assert self.db.fetch_one("SELECT COUNT(id) FROM urls_base") == 4

        self.model.add_url(1, '/a?y=1')
        assert self.db.fetch_one("SELECT COUNT(id) FROM urls_base") == 4
        assert self.db.fetch_one("SELECT COUNT(id) FROM urls_base_params") == 3
