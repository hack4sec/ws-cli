# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Alexey Meshcheryakov <tank1st99@gmail.com>

Kernel class for threading
"""

import threading


class WSThread(threading.Thread):
    """ Kernel class for threading """
    running = True

    def __init__(self, job, result):
        super(WSThread, self).__init__()
        self.job = job
        self.result = result

    def run(self):
        """ Run thread """
        pass
