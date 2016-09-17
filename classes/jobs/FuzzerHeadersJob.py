# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Job class for FuzzerHeaders module
"""

from classes.jobs.MongoJob import MongoJob

class FuzzerHeadersJob(MongoJob):
    """ Job class for FuzzerHeaders module """
    collection_name = 'fuzzer_headers'


