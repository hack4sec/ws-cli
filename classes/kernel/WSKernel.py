# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Alexey Meshcheryakov <tank1st99@gmail.com>

Kernel class
"""

class WSKernel(object):
    """ Kernel class """
    pool = []

    def create_threads(self, threads):
        """ Run threads from list, put it in pool """
        self.pool = threads
        for thread in threads:
            thread.start()

    def finished(self):
        """ Is all threads are finished? """
        for pool in self.pool:
            if pool.running:
                return False
        return True

