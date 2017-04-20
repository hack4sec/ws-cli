# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Thread class for FuzzerHeaders module
"""
from __future__ import division

import threading
import Queue
import time

from requests.exceptions import ConnectionError

from classes.Registry import Registry
from libs.common import file_to_list


class FuzzerHeadersThread(threading.Thread):
    """ Thread class for FuzzerHeaders module """
    queue = None
    method = None
    url = None
    counter = None
    last_action = 0

    def __init__(self, queue, domain, protocol, method, delay, counter, result):
        threading.Thread.__init__(self)
        self.queue = queue
        self.method = method.lower()
        self.domain = domain
        self.result = result
        self.counter = counter
        self.protocol = protocol
        self.done = False
        self.bad_words = file_to_list(Registry().get('wr_path') + "/bases/bad-words.txt")
        self.headers = self._get_headers()
        self.http = Registry().get('http')
        self.delay = int(delay)

    def _get_headers(self):
        return file_to_list(Registry().get('wr_path') + "/bases/fuzzer-headers.txt")

    def run(self):
        """ Run thread """
        req_func = getattr(self.http, self.method)
        need_retest = False

        while True:
            self.last_action = int(time.time())

            if self.delay:
                time.sleep(self.delay)
            try:
                if not need_retest:
                    url = self.queue.get()

                for header in self.headers:
                    try:
                        resp = req_func(
                            "{0}://{1}{2}".format(self.protocol, self.domain, url),
                            headers={header.lower(): Registry().get('fuzzer_evil_value')},
                            #headers={header.lower(): Registry().get('config')['fuzzer']['headers_evil_value']},
                        )
                    except ConnectionError:
                        need_retest = True
                        self.http.change_proxy()
                        continue

                    if resp is None:
                        continue

                    if resp.status_code > 499 and resp.status_code < 600:
                        self.result.append(
                            {"url": url, "words": ["{0} Status code".format(resp.status_code)], "header": header}
                        )
                        continue

                    found_words = []
                    for bad_word in self.bad_words:
                        if resp.content.lower().count(bad_word):
                            found_words.append(bad_word)

                    if len(found_words):
                        self.result.append({"url": url, "words": found_words, "header": header})

                self.counter.up()

                self.queue.task_done(url)
                need_retest = False
            except Queue.Empty:
                self.done = True
                break
            except BaseException as e:
                print url + " " + str(e)
                self.queue.task_done(url)
