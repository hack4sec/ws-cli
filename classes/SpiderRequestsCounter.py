# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Requests counter for Spider module
"""

from classes.Registry import Registry


class SpiderRequestsCounter(object):
    """ Requests counter for Spider module """
    counter = 0
    limit = 0

    def __init__(self, limit):
        self.limit = limit

    def get(self):
        """ Return current count """
        return self.counter

    def up(self):
        """ Up requests counter """
        self.counter += 1

    def allowed(self):
        """ Is more requests allowed (config limit)? """
        allowed = True

        if self.limit and self.counter >= self.limit:
            allowed = False

        return allowed
