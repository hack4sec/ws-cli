# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Common class for all models
"""

from classes.Registry import Registry


class CommonModel(object):
    """ Common class for all models """
    _db = None

    def __init__(self):
        self._db = Registry().get('ndb')

