# -*- coding: utf-8 -*-
""" Kernel class """

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

