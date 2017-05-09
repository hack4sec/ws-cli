# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Unit tests for MongoJob
"""
import sys
import os

wrpath = os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + '/../../')
testpath = os.path.realpath(os.path.dirname(os.path.realpath(__file__)))

sys.path.append(wrpath)
sys.path.append(wrpath + '/classes')
sys.path.append(wrpath + '/classes/jobs')

from Common import Common
from classes.jobs.MongoJob import MongoJob
from classes.Registry import Registry

class JobForTest(MongoJob):
    """Test Job"""
    collection_name = 'testcol'

    def build_row(self, _str):
        return {
            "name": _str.strip(),
            "checked": 0,
            "getted": 0
        }

class Test_MongoJob(Common):
    """Unit tests for MongoJob"""
    model = None

    def setup(self):
        Registry().set('config', {'main': {'mongo_data_load_per_once': 1000}})
        self.model = JobForTest()

    def test_qsize(self):
        self.model.collection.drop()

        assert self.model.qsize() == 0
        self.model.load_dict(['one', 'two', 'three'])
        assert self.model.qsize() == 3
        self.model.task_done('one')
        self.model.task_done('two')
        assert self.model.qsize() == 1
