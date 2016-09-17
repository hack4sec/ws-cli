# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Thread class for FuzzerUrls module (selenium)
"""
from __future__ import division

import Queue
import time

from selenium.common.exceptions import TimeoutException

from classes.Registry import Registry
from classes.threads.SeleniumThread import SeleniumThread
from libs.common import file_to_list


class SFuzzerUrlsThread(SeleniumThread):
    """ Thread class for FuzzerUrls module (selenium) """
    queue = None
    method = None
    url = None
    counter = None
    last_action = 0

    def __init__(
            self, queue, domain, protocol, method, delay, ddos_phrase, ddos_human, recreate_phrase, counter, result
    ):
        super(SFuzzerUrlsThread, self).__init__()
        self.queue = queue
        self.method = method.lower()
        self.domain = domain
        self.result = result
        self.counter = counter
        self.protocol = protocol
        self.done = False
        self.bad_words = file_to_list(Registry().get('wr_path') + "/bases/bad-words.txt")
        self.http = Registry().get('http')
        self.delay = int(delay)
        self.ddos_phrase = ddos_phrase
        self.ddos_human = ddos_human
        self.recreate_phrase = recreate_phrase

        Registry().set('url_for_proxy_check', "{0}://{1}".format(protocol, domain))

        self.browser_create()

    def run(self):
        """ Run thread """
        if self.delay:
            time.sleep(self.delay)
        while True:
            self.last_action = int(time.time())

            try:
                url = self.queue.get()
                self.browser.get(
                    "{0}://{1}{2}".format(self.protocol, self.domain, url)
                )

                found_words = []
                for bad_word in self.bad_words:
                    if self.browser.page_source.count(bad_word):
                        found_words.append(bad_word)

                if len(found_words):
                    self.result.append({"url": url, "words": found_words})

                self.counter.up()
            except Queue.Empty:
                self.done = True
                break
            except TimeoutException as e:
                self.queue.put(url)
                self.browser_close()
                self.browser_create()
                continue
            except BaseException as e:
                if not str(e).count('Timed out waiting for page load'):
                    print url + " " + str(e)
            self.up_requests_count()

        self.browser.close()
