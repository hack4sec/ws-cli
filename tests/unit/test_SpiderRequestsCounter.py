# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Unit tests for SpiderRequestsCounter
"""

from Common import Common
from classes.SpiderRequestsCounter import SpiderRequestsCounter

class Test_SpiderRequestsCounter(Common):
    """Unit tests for SpiderRequestsCounter"""
    model = None

    def setup(self):
        self.model = SpiderRequestsCounter(2)

    def test_main(self):
        assert self.model.get() == 0
        assert self.model.allowed()
        self.model.up()
        assert self.model.get() == 1
        assert self.model.allowed()
        self.model.up()
        assert self.model.get() == 2
        assert not self.model.allowed()
