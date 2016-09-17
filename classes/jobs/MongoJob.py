# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Common class for jobs works with MongoDB
"""

import Queue

from classes.Registry import Registry
from classes.kernel.WSJob import WSJob

class MongoJob(WSJob):
    """ Common class for jobs works with MongoDB """
    unique = True
    collection = None
    select_limit = 50
    skip_blank_rows = True
    counter = 0
    collection_name = None

    def __init__(self, maxsize=0):
        WSJob.__init__(self, maxsize)
        self.collection = Registry().get('mongo')[self.collection_name]

    def build_row(self, _str):
        """ Common build row method for MongoDB """
        return {
            "name": _str.strip(),
            "checked": 0,
            "getted": 0
        }

    def qsize(self):
        """ Size of queue """
        return self.collection.find({"checked": 0}).count()

    def set_unique(self, unique=True):
        """ Enable remove dups in queue """
        self.unique = unique

    def set_skip_blank_rows(self, value=True):
        """ If True - we will skip blank rows then fill queue from dict or file """
        self.skip_blank_rows = value

    def task_done(self, name):
        """ Mark current row as done """
        self.counter += 1
        self.collection.update({'name': str(unicode(name)), "getted": 1}, {"$set": {"checked": 1}})
        WSJob.task_done(self)

    def get(self, block=False, timeout=None):
        """ Get next item from queue """
        if self.empty() or self.qsize() < 50:
            self.load_data()

        if self.empty():
            raise Queue.Empty

        return WSJob.get(self, block, timeout)

    def load_data(self):
        """ Load data into queue from MongoDB """
        data = self.collection.find(
            {"checked": 0, "getted": 0},
            limit=int(Registry().get('config')['main']['mongo_data_load_per_once'])
        )

        for row in data:
            self.put(row['name'])
            self.collection.update({"name": row['name']}, {"$set": {"getted": 1}})

        return True

    def load_dict(self, dict_for_load, drop=True):
        """ Fill collection from dict """
        if drop:
            self.collection.drop()

        counter = 0
        last = "START OF FILE"

        for line in dict_for_load:
            try:
                line = line.strip()
                unicode(line)
                self.collection.insert(self.build_row(line))
            except UnicodeDecodeError:
                _str = " UNICODE ERROR: In file '{0}' skip word '{1}', after word '{2}' !".format(file, line, last)
                if Registry().isset('logger'):
                    Registry().get('logger').log(_str)
                else:
                    print _str

                continue

            counter += 1
            last = line

        self.load_data()

        return counter

    def load_dom(self, dom):
        """ Fill queue from DictOfMask """
        self.collection.drop()
        while True:
            word = dom.get()
            if word is None:
                break
            self.collection.insert(self.build_row(word))
        self.collection.create_index('name', drop_dups=True, unique=self.unique)

        self.load_data()
        return self.collection.count()

    def load_file(self, _file):
        """ Fill queue from text file """
        self.collection.drop()

        fh = open(_file)

        last = "START OF FILE"
        while True:
            line = fh.readline()
            if not line:
                break
            if not line.strip() and self.skip_blank_rows:
                continue

            try:
                line = line.strip()
                unicode(line)
                self.collection.insert(self.build_row(line))
            except UnicodeDecodeError:
                _str = " UNICODE ERROR: In file '{0}' skip word '{1}', after word '{2}' !".format(_file, line, last)
                if Registry().isset('logger'):
                    Registry().get('logger').log(_str)
                else:
                    print _str
                continue

            last = line

        fh.close()

        self.collection.create_index('name', drop_dups=True, unique=self.unique)

        self.load_data()

        return self.collection.count()

    # 2 метода ниже взяты с
    # http://stackoverflow.com/questions/1581895/how-check-if-a-task-is-already-in-python-queue
    # Рецепт для уникальных задачь в очереди
    def _init(self, maxsize):
        WSJob._init(self, maxsize)
        if self.unique:
            self.all_items = set()

    def _put(self, item):
        if self.unique:
            if item not in self.all_items:
                WSJob._put(self, item)
                self.all_items.add(item)
            else:
                _str = "WARNING: try to add not unique item `{0}`".format(item)

                if Registry().isset('logger'):
                    #Registry().get('logger').log(_str)
                    pass
                else:
                    #print _str
                    pass
        else:
            WSJob._put(self, item)
