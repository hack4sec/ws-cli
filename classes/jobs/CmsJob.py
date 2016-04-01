# -*- coding: utf-8 -*-
""" Job class for Cms module """

import Queue


class CmsJob(Queue.Queue):
    """ Job class for Cms module """

    def get(self, block=True, timeout=None):
        """ Get next item from queue """
        return Queue.Queue.get(self, False, None)
