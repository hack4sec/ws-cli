#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, unittest, configparser, mysql.connector

wrpath   = os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + '/../../')
testpath = os.path.realpath(os.path.dirname(os.path.realpath(__file__)))

sys.path.append(wrpath)
sys.path.append(wrpath + '/classes')
sys.path.append(testpath + '/classes')
sys.path.append(wrpath + '/classes/models')
sys.path.append(wrpath + '/classes/jobs')
sys.path.append(wrpath + '/classes/threads')
sys.path.append(wrpath + '/classes/kernel')

#from CommonTest import CommonTest
from classes.Database import Database
from libs.common import *
import pytest

class Test_Database(object):
    model = None
    db = None

    def setup(self):
        config = configparser.ConfigParser()
        config.read(testpath + '/' + 'config.ini')

        self.db = Database(config['db']['host'], config['db']['user'], config['db']['pass'], config['db']['database'])

        self.db.q("DROP TABLE IF EXISTS `test`")
        self.db.q(
            "CREATE TABLE `test` (\
             `id` int(11) NOT NULL AUTO_INCREMENT,\
             `name` varchar(200) NOT NULL,\
             `tested` tinyint(1) NOT NULL DEFAULT '0',\
              PRIMARY KEY (`id`)\
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;"
        )

    def teardown(self):
        self.db.q("DROP TABLE IF EXISTS `test`")
        self.db.close()

    def test_fetch_one(self):
        assert self.db.fetch_one("SELECT 1") == 1

    def test_fetch_all(self):
        data = self.db.fetch_all("SELECT 1 as a, 2 as b UNION SELECT 3 as a, 4 as b")
        compare = [
            {'a': 1, 'b': 2},
            {'a': 3, 'b': 4},
        ]
        assert compare == data

    def test_fetch_col(self):
        data = self.db.fetch_col("SELECT 1 as a, 2 as b UNION SELECT 3 as a, 4 as b")
        compare = [1, 3]
        assert compare == data

    def test_fetch_row(self):
        data = self.db.fetch_row("SELECT 1 as a, 2 as b UNION SELECT 3 as a, 4 as b")
        compare = {'a': 1, 'b': 2}

        assert compare == data

    def atest_fetch_pairs(self):
        data = self.db.fetch_pairs("SELECT 1 as a, 2 as b UNION SELECT 3 as a, 4 as b")
        compare = {1: 2, 3: 4}

        assert compare == data

    def test_escape(self):
        assert self.db.escape(r"a\b'c") == r"a\\b\'c"

    def test_quote(self):
        assert self.db.quote(r"a\b'c") == r"'a\\b\'c'"

    def test_q(self):
        curs = self.db.q("SELECT 1", True)
        assert curs.__class__.__name__ == 'MySQLCursor'
        curs.fetchall()
        curs.close()

    def test_insert(self):
        assert self.db.fetch_one("SELECT COUNT(id) FROM `test`") == 0
        self.db.insert('test', {'name': 'aaa'})
        assert self.db.fetch_one("SELECT COUNT(id) FROM `test`") == 1

        with pytest.raises(mysql.connector.IntegrityError):
            self.db.insert('test', {'id': 1, 'name': 'aaa'})

        self.db.insert('test', {'id': 1, 'name': 'aaa'}, ignore=True) # Without ex

    def test_insert_mass(self):
        assert self.db.fetch_one("SELECT COUNT(id) FROM `test`") == 0

        data = []
        for i in range(1, 75):
            data.append({'id': i, 'name': 'aaa' + str(i)})
        self.db.insert_mass('test', data)
        assert self.db.fetch_one("SELECT COUNT(id) FROM `test`") == 74

        self.db.q("TRUNCATE TABLE `test`")

        data = []
        for i in range(1, 30):
            data.append({'id': i, 'name': 'aaa' + str(i)})
        self.db.insert_mass('test', data)
        assert self.db.fetch_one("SELECT COUNT(id) FROM `test`") == 29

        data = []
        for i in range(1, 30):
            data.append({'id': i, 'name': 'aaa' + str(i)})
        with pytest.raises(mysql.connector.IntegrityError):
            self.db.insert_mass('test', data)

        data = []
        for i in range(1, 30):
            data.append({'id': i, 'name': 'aaa' + str(i)})
        self.db.insert_mass('test', data, ignore=True)

    def test_update(self):
        self.db.insert('test', {'name': 'aaa'})
        self.db.insert('test', {'name': 'bbb'})
        self.db.insert('test', {'name': 'ccc'})
        assert self.db.fetch_one("SELECT COUNT(id) FROM `test` WHERE `tested`=0") == 3
        self.db.update('test', {'tested': 1}, "`name`='aaa'")
        assert self.db.fetch_one("SELECT COUNT(id) FROM `test` WHERE `tested`=0") == 2

    def test_update_mass(self):
        data = []
        for i in range(1, 30):
            data.append({'id': i, 'name': 'aaa' + str(i)})
        self.db.insert_mass('test', data)
        assert self.db.fetch_one("SELECT COUNT(id) FROM `test` WHERE `tested`=0") == 29
        self.db.update_mass('test', 'tested', {"`name`='aaa1'": 1, "`name`='aaa2'": 1, "`name`='aaa3'": 1, })
        assert self.db.fetch_one("SELECT COUNT(id) FROM `test` WHERE `tested`=0") == 26

    def test_replace(self):
        assert self.db.fetch_one("SELECT COUNT(id) FROM `test`") == 0
        self.db.insert('test', {'id': 1, 'name': 'aaa'})
        assert self.db.fetch_one("SELECT COUNT(id) FROM `test` WHERE `name`='aaa' AND `id`=1") == 1
        self.db.replace('test', {'id': 1, 'name': 'aaa1'})
        assert self.db.fetch_one("SELECT COUNT(id) FROM `test` WHERE `name`='aaa1' AND `id`=1") == 1
