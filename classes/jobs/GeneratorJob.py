# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Common job class for generator jobs
"""
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
