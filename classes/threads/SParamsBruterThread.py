# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Thread class for Dafs modules (selenium)
"""

import Queue
import time
import re
import pprint

from selenium.common.exceptions import TimeoutException

from classes.Registry import Registry
from classes.threads.SeleniumThread import SeleniumThread

class SParamsBruterThread(SeleniumThread):
    """ Thread class for Dafs modules (selenium) """
    queue = None
    method = None
    template = None
    mask_symbol = None
    counter = None
    last_action = 0
    queue_is_empty = False
    last_word = ""

    def __init__(
            self, queue, protocol, host, url, max_params_length, value, method, mask_symbol, not_found_re,
            delay, ddos_phrase, ddos_human, recreate_re, ignore_words_re, counter, result
    ):
        super(SParamsBruterThread, self).__init__()
        self.queue = queue
        self.protocol = protocol.lower()
        self.host = host
        self.method = 'get'
        self.url = url
        self.max_params_length = int(max_params_length)
        self.mask_symbol = mask_symbol
        self.counter = counter
        self.result = result
        self.value = value
        self.done = False
        self.not_found_re = False if not len(not_found_re) else re.compile(not_found_re)
        self.recreate_re = False if not len(recreate_re) else re.compile(recreate_re)
        self.http = Registry().get('http')
        self.delay = int(delay)
        self.ddos_phrase = ddos_phrase
        self.ddos_human = ddos_human
        self.ignore_words_re = False if not len(ignore_words_re) else re.compile(ignore_words_re)

        Registry().set('url_for_proxy_check', "{0}://{1}".format(protocol, host))

        self.browser_create()

        self.logger = Registry().get('logger')

    def build_params_str(self):
        params_str = "" if not len(self.last_word) else "{0}={1}&".format(self.last_word, self.value)
        self.last_word = ""
        while len(params_str) < self.max_params_length:
            try:
                word = self.queue.get()
            except Queue.Empty:
                self.queue_is_empty = True
                break

            if not len(word.strip()) or (self.ignore_words_re and self.ignore_words_re.findall(word)):
                continue

            self.counter.up()

            params_str += "{0}={1}&".format(word, self.value)

            self.last_word = word

        return params_str[:-(len(self.last_word) + 3)]

    def run(self):
        """ Run thread """
        need_retest = False

        while not self.done:
            self.last_action = int(time.time())

            if self.delay:
                time.sleep(self.delay)

            try:
                if not need_retest:
                    params_str = params_str = self.build_params_str()

                self.browser.get(self.protocol + "://" + self.host + self.url + params_str)

                if self.recreate_re and self.recreate_re.findall(self.browser.page_source):
                    need_retest = True
                    self.browser_close()
                    self.browser_create()
                    continue

                positive_item = False
                if not self.not_found_re.findall(self.browser.page_source):
                    param_found = False
                    for one_param in params_str.split("&"):
                        self.browser.get(self.protocol + "://" + self.host + self.url + one_param)

                        if not self.not_found_re.findall(self.browser.page_source):
                            self.result.append(one_param)
                            param_found = True
                            found_item = one_param

                    if param_found is False:
                        self.result.append(params_str)
                        found_item = params_str

                    positive_item = True

                    self.logger.item(found_item, self.browser.page_source, True, positive=positive_item)

                if len(self.result) >= int(Registry().get('config')['main']['positive_limit_stop']):
                    Registry().set('positive_limit_stop', True)

                need_retest = False

                if self.queue_is_empty:
                    self.done = True
                    break
            except UnicodeDecodeError as e:
                self.logger.ex(e)
                need_retest = False
            except TimeoutException as e:
                need_retest = True
                self.browser_close()
                self.browser_create()
                continue
            except BaseException as e:
                try:
                    need_retest = True
                    if len(e.args) and e.args[0] == 111:
                        self.browser_close()
                        self.browser_create()
                    elif not str(e).count('Timed out waiting for page load'):
                        self.logger.ex(e)
                except UnicodeDecodeError:
                    need_retest = False
            self.up_requests_count()

        self.browser_close()
