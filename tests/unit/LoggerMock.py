# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Mock for Logger
"""
class LoggerMock(object):
    """Mock for Logger"""
    def log(self, _str):
        pass

    def ex(self, e):
        raise Exception(e)

    def item(self, a, b, c, positive):
        pass