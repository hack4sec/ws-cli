# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Unit tests for ProjectsModel
"""
import sys
import os

wrpath = os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + '/../')
testpath = os.path.realpath(os.path.dirname(os.path.realpath(__file__)))

sys.path.append(wrpath + '/classes')
sys.path.append(wrpath + '/classes/models')

from Common import Common
from classes.models.ProjectsModel import ProjectsModel


class Test_ProjectsModel(Common):
    """Unit tests for ProjectsModel"""
    model = None

    def setup(self):
        self.model = ProjectsModel()
        self.db.q("TRUNCATE TABLE `projects`")

    def test_get_by_name(self):
        self.db.q("INSERT INTO projects (id, name, descr) VALUES(1, 'prj', '')")
        test_data = {'id': 1, 'name': 'prj', 'descr': ''}
        assert self.model.get_by_name('prj') == test_data

    def test_exists(self):
        self.db.q("INSERT INTO projects (id, name, descr) VALUES(1, 'prj', '')")
        assert self.model.exists('prj')
        assert not self.model.exists('prj2')

    def test_create(self):
        assert not self.model.exists('prj')

        _id = self.model.create('prj', '')
        assert _id == 1

        assert self.model.exists('prj')

    def test_list(self):
        self.db.q("INSERT INTO projects (id, name, descr) VALUES(1, 'prj1', 'a')")
        self.db.q("INSERT INTO projects (id, name, descr) VALUES(2, 'prj2', 'b')")
        self.db.q("INSERT INTO projects (id, name, descr) VALUES(3, 'prj3', 'c')")

        test_data = [
            {'id': 1, 'name': 'prj1', 'descr': 'a'},
            {'id': 2, 'name': 'prj2', 'descr': 'b'},
            {'id': 3, 'name': 'prj3', 'descr': 'c'},
        ]

        assert test_data == self.model.list()

    def test_delete(self):
        self.db.q("INSERT INTO projects (id, name, descr) VALUES(1, 'prj', '')")
        assert self.model.exists('prj')
        self.model.delete('prj')
        assert not self.model.exists('prj')
