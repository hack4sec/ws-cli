# -*- coding: utf-8 -*-
""" Job class for FuzzerHeaders module """

from classes.jobs.MongoJob import MongoJob

class FuzzerHeadersJob(MongoJob):
    """ Job class for FuzzerHeaders module """
    collection_name = 'fuzzer_headers'


