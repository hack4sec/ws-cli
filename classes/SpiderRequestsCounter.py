# -*- coding: utf-8 -*-
""" Requests counter for Spider module """

from classes.Registry import Registry


class SpiderRequestsCounter(object):
    """ Requests counter for Spider module """
    counter = 0
    limit = 0

    def __init__(self):
        self.limit = int(Registry().get('config')['spider']['requests_limit'])

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
