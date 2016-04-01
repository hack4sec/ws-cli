# -*- coding: utf-8 -*-
""" Class of registry """

class Registry(object):
    """ Class of registry """
    data = {}

    def get(self, key):
        """ Get data from registry """
        return Registry.data[key]

    def set(self, key, value):
        """ Set data to registry """
        Registry.data[key] = value

    def isset(self, key):
        """ Is key in registry? """
        return key in Registry.data
