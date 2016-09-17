# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Job class for Cms module
"""

import Queue


class CmsJob(Queue.Queue):
    """ Job class for Cms module """

    def get(self, block=True, timeout=None):
        """ Get next item from queue """
        return Queue.Queue.get(self, False, None)
