#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, pprint

wrpath   = os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + '/../../')
testpath = os.path.realpath(os.path.dirname(os.path.realpath(__file__)))

sys.path.append(wrpath)
sys.path.append(wrpath + '/classes')
sys.path.append(wrpath + '/classes/jobs')

from ModelsCommon import ModelsCommon
from classes.jobs.MongoJob import MongoJob
from libs.common import *

class JobForTest(MongoJob):
    collection_name = 'testcol'

    def build_row(self, str):
        return {
            "name": str.strip(),
            "checked": 0,
            "getted": 0
        }

class Test_MongoJob(ModelsCommon):
    model = None

    def setup(self):
        Registry().set('config', {'main': {'mongo_data_load_per_once': 1000}})
        self.model = JobForTest()

    # Проверка вывода верного размера очереди из MongoDB
    def test_qsize(self):
        pprint.pprint(1)
        self.model.collection.drop()

        assert self.model.qsize() == 0
        pprint.pprint(12)
        self.model.load_dict(['one', 'two', 'three'])
        assert self.model.qsize() == 3
        pprint.pprint(3)
        self.model.task_done('one')
        self.model.task_done('two')
        assert self.model.qsize() == 1
        pprint.pprint(4)
