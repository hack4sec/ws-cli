# -*- coding: utf-8 -*-
""" Job class for DnsBrute* modules """

from classes.jobs.GeneratorJob import GeneratorJob

class DnsBruteJob(GeneratorJob):
    """ Job class for DnsBrute* modules """
    collection_name = 'dns_brute_names'
