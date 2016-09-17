# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Class of registry
"""

class Registry(object):
    """ Class of registry """
    data = {}

    def get(self, key):
        """ Get data from registry """
        return Registry.data[key]

    def set(self, key, value):
        """ Set data to registry """
        Registry.data[key] = value

    def isset(self, key):
        """ Is key in registry? """
        return key in Registry.data
