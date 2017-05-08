# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Thread class for Spider module
"""
import Queue
import time

from classes.Registry import Registry
from classes.SpiderCommon import SpiderCommon
from classes.kernel.WSThread import WSThread
from classes.SpiderLinksParser import SpiderLinksParser
from libs.common import file_put_contents, md5


class SpiderThread(WSThread):
    """ Thread class for Spider module """
    last_action = 0

    def __init__(self, job, host, protocol, src, delay, counter):
        WSThread.__init__(self, None, None)
        self.job = job
        self.host = host
        self.protocol = protocol
        self.links_parser = SpiderLinksParser()
        #self.not_found_phrase = not_found_phrase
        self.http = Registry().get('http')
        self.src = src
        self.delay = int(delay)
        self.counter = counter
        self._db = Registry().get('mongo')

    def run(self):
        """ Run thread """
        while self.src.allowed():
            self.counter.all = self.job.qsize()
            try:
                links = self.job.get_many()
                self.scan_links(links)
            except Queue.Empty:
                break
        self.running = False

    def _checked(self, link):
        """ Mark link as checked """
        del link['_id']
        self._db.spider_urls.update({'hash': link['hash']}, {'$set': link})

    def scan_links(self, links):
        """ Scan links """
        req_func = getattr(self.http, 'get')

        for link in links:
            self.last_action = int(time.time())

            self.counter.up()

            url = SpiderCommon.gen_url(link, self.host, self.protocol)

            start_time = int(round(time.time() * 1000))

            pre_url = link['path'] + '?' + link['query'] if len(link['query']) else link['path']

            if self.delay:
                time.sleep(self.delay)

            response = req_func(url)
            self.src.up()
            if response is not None:
                result_time = int(round(time.time() * 1000)) - start_time
                if 'content-type' in response.headers:
                    content_type = response.headers['content-type'].split(";")[0] \
                                   if (response.headers['content-type'].find(";") != -1) \
                                   else response.headers['content-type']
                else:
                    content_type = 'unknown/unknown'

                if 299 < response.status_code < 400:
                    SpiderCommon.insert_links([response.headers['Location']], url, self.host)
                else:
                    new_links = self.links_parser.parse_links(content_type, str(response.content), link)
                    SpiderCommon.insert_links(new_links, url, self.host)

                file_put_contents(
                    "{0}{1}/{2}".format(
                        Registry().get('data_path'),
                        self.host,
                        md5(pre_url)
                    ),
                    str(response.content)
                )

            link['size'] = len(response.content) if response is not None else 0
            link['code'] = response.status_code if response is not None else 0
            link['time'] = result_time if response is not None else 0

        SpiderCommon.links_checked(links)


