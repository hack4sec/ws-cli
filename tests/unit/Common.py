# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Common class for unit tests
"""

import sys
import os
import configparser
import mysql.connector
import pymongo.errors
from pymongo import MongoClient

wrpath = os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + '/../../')
testpath = os.path.realpath(os.path.dirname(os.path.realpath(__file__)))

sys.path.append(wrpath)
sys.path.append(wrpath + '/classes')
sys.path.append(testpath + '/classes')
sys.path.append(wrpath + '/classes/models')
sys.path.append(wrpath + '/classes/jobs')
sys.path.append(wrpath + '/classes/threads')
sys.path.append(wrpath + '/classes/kernel')

from classes.Database import Database
from classes.Registry import Registry
from classes.Proxies import Proxies


class Common(object):
    """Common class for unit tests"""
    threads_max_work_time = 60

    def setup_class(self):
        config = configparser.ConfigParser()
        config.read('config.ini')

        try:
            db = mysql.connector.connect(
                host=config['db']['host'],
                user=config['db']['user'],
                password=config['db']['pass'],
                database=config['db']['database']
            )
            db.autocommit = True
        except mysql.connector.errors.ProgrammingError as e:
            print " ERROR: Can`t connect to MySQL server! ({0})".format(str(e))
            exit(0)

        try:
            mc = MongoClient(host=config['mongo']['host'], port=int(config['mongo']['port']))
            mongo_collection = getattr(mc, config['mongo']['collection'])
        except pymongo.errors.ConnectionFailure as e:
            print " ERROR: Can`t connect to MongoDB server! ({0})".format(str(e))
            exit(0)

        R = Registry()
        R.set('config', config)
        R.set('db', db)
        R.set('mongo', mongo_collection)
        R.set('wr_path', wrpath)
        R.set('data_path', wrpath + '/data/')
        R.set('ndb',
              Database(config['db']['host'], config['db']['user'], config['db']['pass'], config['db']['database']))
        R.set('proxies', Proxies())

        self.db = R.get('ndb')

    def teardown(self):
        self.db.q("TRUNCATE TABLE urls")
        self.db.q("TRUNCATE TABLE urls_base")
        self.db.q("TRUNCATE TABLE urls_base_params")
        self.db.q("TRUNCATE TABLE projects")
        self.db.q("TRUNCATE TABLE hosts")
        self.db.q("TRUNCATE TABLE ips")

        Registry().get('mongo').spider_urls.drop()
