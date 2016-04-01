# -*- coding: utf-8 -*-
""" Job class for Spider module """

import Queue
import time

from classes.Registry import Registry
from classes.kernel.WSJob import WSJob
from libs.common import mongo_result_to_list


class SpiderJob(WSJob):
    """ Job class for Spider module """
    get_blocked = False

    def __init__(self, maxsize=0):
        WSJob.__init__(self, maxsize)
        self._db = Registry().get('mongo')

    def _fill_queue(self):
        """ Inner method for fill mongo collection """
        links = self._db.spider_urls.find({'checked': 0, 'getted': 0}).limit(10)
        links = mongo_result_to_list(links)

        if len(links):
            for link in links:
                link['getted'] = 1
                self._db.spider_urls.update({'hash': link['hash']}, {'$set': {'getted': 1}})

            for link in links:
                self.put(link)

    def get(self, block=True, timeout=None):
        """ Get next element from queue """
        if self.empty():
            while self.get_blocked:
                time.sleep(1)
            self.get_blocked = True
            self._fill_queue()
            self.get_blocked = False

        if self.empty():
            raise Queue.Empty

        return WSJob.get(self, block, timeout)

    def get_many(self):
        """ Get many next elements from queue """
        result = []
        try:
            while len(result) < int(Registry().get('config')['spider']['links_one_time_in_work']):
                result.append(self.get())
        except Queue.Empty:
            if not len(result):
                raise Queue.Empty

        return result

    def have_work_links(self):
        """ Are we have any work elements in collection? """
        return bool(self._db.spider_urls.find({'checked': 0}).count())

    def qsize(self):
        """ Size of queue """
        return self._db.spider_urls.find({'checked': 0}).count()

