# -*- coding: utf-8 -*-
""" Common job class for generator jobs """
import Queue

class GeneratorJob(object):
    """ Job class for DnsBrute* modules """
    collection_name = None
    generator = None

    def set_generator(self, generator):
        """ Set work generator """
        self.generator = generator

    def get(self):
        """ Get next generator word """
        word = self.generator.get()
        if word is None:
            raise Queue.Empty
        return word
