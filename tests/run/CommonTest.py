# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Common class tests
"""
import os
import shutil
import subprocess

import configparser
import mysql.connector
import pymongo.errors
from pymongo import MongoClient


from classes.Registry import Registry
from classes.Database import Database

wrpath = os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + '/../../')
testpath = os.path.realpath(os.path.dirname(os.path.realpath(__file__)))


class CommonTest(object):
    """ Common class tests """
    db = None

    def setup_class(self):
        open(wrpath + '/proxies.list', 'w').close()

        config = configparser.ConfigParser()
        config.read(os.getcwd() + '/' + 'config.ini')

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

        self.db = Registry().get('ndb')

    def setup(self):
        self.clear_db()

    def clear_db(self):
        """ Clearing db """
        self.db.q("TRUNCATE TABLE `hosts`")
        self.db.q("TRUNCATE TABLE `ips`")
        self.db.q("TRUNCATE TABLE `projects`")
        self.db.q("TRUNCATE TABLE `urls`")
        self.db.q("TRUNCATE TABLE `requests`")
        self.db.q("TRUNCATE TABLE `hosts_info`")
        self.db.q("TRUNCATE TABLE `urls_base`")
        self.db.q("TRUNCATE TABLE `urls_base_params`")
        self.db.q("TRUNCATE TABLE `cms`")
        self.db.q("TRUNCATE TABLE `cms_paths`")
        self.db.q("TRUNCATE TABLE `cms_paths_hashes`")

    def output_errors(self, out):
        """
        Check output for errors
        :param out: output
        :return:
        """
        assert out.find("Traceback") == -1
        assert "killed by time" not in out

    def _replace_config(self, name):
        """
        Change work config
        :param name: config name (*.ini)
        :return:
        """
        shutil.copyfile("{0}/config.ini".format(wrpath), "{0}/config.ini.bak".format(wrpath))
        shutil.copyfile("{0}/configs/{1}.ini".format(testpath, name), "{0}/config.ini".format(wrpath))

    def _restore_config(self):
        """ Restore old original config """
        shutil.move("{0}/config.ini.bak".format(wrpath), "{0}/config.ini".format(wrpath))

    def _run(self, config_name, run_params):
        """
        Run WS
        :param config_name: name of config for test
        :param run_params: params for run WS-process
        :return: output of WS
        """
        self._replace_config(config_name)
        os.chdir(wrpath)
        out = subprocess.check_output(run_params)
        self._restore_config()
        self.output_errors(out)

        return out
