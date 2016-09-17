# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Thread class for Spider module (selenium)
"""
import time
import Queue
import re

from libs.common import file_put_contents, md5
from classes.Registry import Registry
from classes.SpiderCommon import SpiderCommon
from classes.SpiderLinksParser import SpiderLinksParser
from classes.threads.SeleniumThread import SeleniumThread


class SSpiderThread(SeleniumThread):
    """ Thread class for Spider module (selenium) """
    last_action = 0

    def __init__(self, job, host, src, not_found_re, delay, ddos_phrase, ddos_human, recreate_re, counter):
        super(SSpiderThread, self).__init__()

        self._db = Registry().get('mongo')
        self.job = job
        self.host = host
        self.links_parser = SpiderLinksParser()
        self.not_found_re = False if not len(not_found_re) else re.compile(not_found_re)
        self.http = Registry().get('http')
        self.delay = int(delay)
        self.counter = counter
        self.src = src
        self.running = True
        self.ddos_phrase = ddos_phrase
        self.ddos_human = ddos_human
        self.recreate_re = False if not len(recreate_re) else re.compile(recreate_re)

        Registry().set('url_for_proxy_check', "{0}://{1}".format('http', host))

        self.browser_create()

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
        self.browser_close()

    def _checked(self, link):
        """  Mark link as checeked  """
        del link['_id']
        self._db.spider_urls.update({'hash': link['hash']}, {'$set': link})

    def scan_links(self, links):
        """ Scan links """
        for link in links:
            self.last_action = int(time.time())

            url = SpiderCommon.gen_url(link, self.host)

            start_time = int(round(time.time() * 1000))

            pre_url = link['path'] + '?' + link['query'] if len(link['query']) else link['path']

            if self.delay:
                time.sleep(self.delay)

            try:
                self.browser.get(url)
                time.sleep(1)

                    #content_type = response.headers['content-type'].split(";")[0] \
                    #               if (response.headers['content-type'].find(";") != -1) \
                    #               else response.headers['content-type']

                    #if 299 < response.status_code < 400:
                    #    SpiderCommon.insert_links([response.headers['Location']], url, self.host)
                    #else:
                        #new_links = self.links_parser.parse_links('text/html', str(self.browser.page_source), link)
                        #SpiderCommon.insert_links(new_links, url, self.host)
                source = str(self.browser.page_source.encode('utf8', errors='ignore'))
                new_links = self.links_parser.parse_links('text/html', source, link)
                SpiderCommon.insert_links(new_links, url, self.host)
                if self.not_found_re.findall(self.browser.page_source):
                    link['code'] = 404

                result_time = int(round(time.time() * 1000)) - start_time

                file_put_contents("{0}{1}/{2}".format(
                    Registry().get('data_path'),
                    self.host,
                    md5(pre_url)
                ), str(self.browser.page_source.encode('utf-8')))

                link['size'] = len(self.browser.page_source)

                link['time'] = result_time
                if int(link['code']) == 0:
                    del link['code']
            except BaseException as e:
                if not str(e).count('Timed out waiting for page load'):
                    print str(e)
            self.up_requests_count()

        SpiderCommon.links_checked(links)



