# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Thread class for BF module
"""
import threading
import Queue
import time
import re

from requests.exceptions import ChunkedEncodingError, ConnectionError

from libs.common import is_binary_content_type
from classes.Registry import Registry


class BackupsFinderThread(threading.Thread):
    """ Thread class for BF module """
    queue = None
    method = None
    url = None
    counter = None
    last_action = 0

    def __init__(self, queue, domain, protocol, method, not_found_re, not_found_codes,
                 not_found_size, delay, counter, result):
        threading.Thread.__init__(self)
        self.queue = queue
        self.domain = domain
        self.result = result
        self.counter = counter
        self.protocol = protocol
        self.not_found_re = False if not len(not_found_re) else re.compile(not_found_re)
        self.not_found_size = int(not_found_size)
        self.method = method if \
            not ((len(not_found_re) or self.not_found_size != -1) and method.lower() == 'head') else \
            'get'

        not_found_codes = not_found_codes.split(',')
        not_found_codes.append('404')
        self.not_found_codes = list(set(not_found_codes))

        self.delay = int(delay)

        self.done = False
        self.http = Registry().get('http')
        self.logger = Registry().get('logger')

    def run(self):
        """ Run thread """
        req_func = getattr(self.http, self.method)
        need_retest = False

        while not self.done:
            self.last_action = int(time.time())

            if self.delay:
                time.sleep(self.delay)
            try:
                if not need_retest:
                    word = self.queue.get()
                    self.counter.up()

                url = "{0}://{1}{2}".format(self.protocol, self.domain, word)

                try:
                    resp = req_func(url)
                except ConnectionError:
                    need_retest = True
                    self.http.change_proxy()
                    continue

                binary_content = resp is not None and is_binary_content_type(resp.headers['content-type'])

                positive_item = False
                if resp is not None \
                    and (self.not_found_size == -1 or self.not_found_size != len(resp.content)) \
                    and str(resp.status_code) not in self.not_found_codes \
                    and not (not binary_content and self.not_found_re and self.not_found_re.findall(resp.content)):
                    self.result.append(word)
                    positive_item = True

                self.logger.item(
                    word,
                    resp.content if not resp is None else "",
                    binary_content,
                    positive=positive_item
                )

                if len(self.result) >= int(Registry().get('config')['main']['positive_limit_stop']):
                    Registry().set('positive_limit_stop', True)

                #self.queue.task_done(word)
                need_retest = False
            except Queue.Empty:
                self.done = True
                break
            except ChunkedEncodingError as e:
                self.logger.ex(e)
            except BaseException as e:
                self.logger.ex(e)
                #self.queue.task_done(word)
