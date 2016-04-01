# -*- coding: utf-8 -*-
""" Kernel class for threading """

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
