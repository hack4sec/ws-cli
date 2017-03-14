# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Alexey Meshcheryakov <tank1st99@gmail.com>

Kernel base class. Prepare work, load config, connect db, etc
"""

import sys
import os
import random

import configparser
import mysql.connector
from pymongo import MongoClient
import pymongo.errors
from pyvirtualdisplay import Display

from libs.common import file_get_contents
from classes.Http import Http
from classes.Database import Database
from classes.Proxies import Proxies
from classes.kernel.WSKernel import WSKernel
from classes.kernel.WSException import WSException
from classes.Registry import Registry

class WSBase(object):
    """ Kernel base class. Prepare work, load config, connect db, etc """
    def __init__(self):
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
        R.set('wr_path', os.getcwd())
        R.set('data_path', os.getcwd() + '/data/')
        R.set('http', Http())
        R.set('ua', self.random_ua())
        R.set('proxies', Proxies())
        R.set(
            'ndb',
            Database(config['db']['host'], config['db']['user'], config['db']['pass'], config['db']['database'])
        )
        R.set(
            'fuzzer_evil_value',
            file_get_contents(Registry().get('wr_path') + "/bases/fuzzer-evil-value.txt").strip()
        )
        R.set('proxy_many_died', False)
        R.set('positive_limit_stop', False)

        if " ".join(sys.argv).count('selenium') and int(config['selenium']['virtual_display']):
            display = Display(visible=0, size=(800, 600))
            display.start()
            R.set('display', display)

    def random_ua(self):
        fh = open(Registry().get('wr_path') + "/bases/useragents.txt", 'r')
        uas = fh.readlines()
        fh.close()

        return uas[random.randint(0, len(uas) - 1)].strip()

    def __my_import(self, name):
        """ Load need WS module """
        if not os.path.exists('classes/modules/' + name + '.py'):
            raise WSException

        sys.path.append('classes/modules/')
        mod = __import__(name)
        the_class = getattr(mod, name)
        return the_class

    def load_module(self, modulename):
        """ Public method for load module """
        module = self.__my_import(modulename)
        kernel = WSKernel()
        moduleclass = module(kernel)
        return moduleclass

    def get_modules_list(self):
        """ Return list of available modules """
        return list(map(lambda x: os.path.splitext(x)[0], filter(lambda x: x.endswith('py'), os.listdir('modules/'))))
