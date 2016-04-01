# -*- coding: utf-8 -*-
""" Common class for all models """

from classes.Registry import Registry


class CommonModel(object):
    """ Common class for all models """
    _db = None

    def __init__(self):
        self._db = Registry().get('ndb')

