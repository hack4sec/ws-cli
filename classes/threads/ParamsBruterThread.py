# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Thread class for Dafs modules
"""

import threading
import Queue
import time
import copy
import re
import pprint

from requests.exceptions import ChunkedEncodingError, ConnectionError
from classes.threads.HttpThread import HttpThread

from classes.Registry import Registry


class ParamsBruterThread(HttpThread):
    """ Thread class for ParamsBrute modules """
    queue = None
    method = None
    template = None
    mask_symbol = None
    counter = None
    retested_words = None
    last_action = 0
    retest_limit = int(Registry().get('config')['dafs']['retest_limit'])
    ignore_words_re = None
    queue_is_empty = False
    last_word = ""

    def __init__(
            self, queue, protocol, host, url, max_params_length, value, method, mask_symbol, not_found_re,
            not_found_size, not_found_codes, retest_codes, delay, ignore_words_re,
            counter, result):
        super(ParamsBruterThread, self).__init__()
        self.retested_words = {}

        self.queue = queue
        self.protocol = protocol.lower()
        self.host = host
        self.url = url
        self.mask_symbol = mask_symbol
        self.counter = counter
        self.result = result
        self.value = value
        self.done = False
        self.max_params_length = int(max_params_length)
        self.ignore_words_re = False if not len(ignore_words_re) else re.compile(ignore_words_re)
        self.not_found_re = False if not len(not_found_re) else re.compile(not_found_re)
        self.not_found_size = int(not_found_size)
        self.method = method.lower()

        not_found_codes = not_found_codes.split(',')
        not_found_codes.append('404')
        self.not_found_codes = list(set(not_found_codes))
        self.retest_codes = list(set(retest_codes.split(','))) if len(retest_codes) else []

        self.delay = int(delay)
        self.retest_delay = int(Registry().get('config')['params_bruter']['retest_delay'])

        self.http = copy.deepcopy(Registry().get('http'))
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

    def request_params(self, params):
        full_url = self.protocol + "://" + self.host + self.url
        return self.http.get(full_url + params) if \
            self.method == 'get' else \
            self.http.post(full_url, data=params, headers={'Content-Type': 'application/x-www-form-urlencoded'})

    def run(self):
        """ Run thread """
        need_retest = False

        while not self.done:
            self.last_action = int(time.time())

            if self.delay:
                time.sleep(self.delay)

            try:
                if not need_retest:
                    params_str = self.build_params_str()

                try:
                    resp = self.request_params(params_str)
                except ConnectionError:
                    need_retest = True
                    self.http.change_proxy()
                    continue

                if self.is_retest_need(params_str, resp):
                    time.sleep(self.retest_delay)
                    need_retest = True
                    continue

                positive_item = False
                if self.is_response_right(resp):
                    param_found = False
                    for one_param in params_str.split("&"):
                        try:
                            resp = self.request_params(one_param)
                        except ConnectionError:
                            need_retest = True
                            self.http.change_proxy()
                            continue

                        if self.is_response_right(resp):
                            self.result.append(one_param)
                            param_found = True
                            found_item = one_param

                    if param_found is False:
                        self.result.append(params_str)
                        found_item = params_str

                    positive_item = True

                    self.log_item(found_item, resp, positive_item)

                self.check_positive_limit_stop(self.result)

                need_retest = False

                if self.queue_is_empty:
                    self.done = True
                    break
            except ChunkedEncodingError as e:
                self.logger.ex(e)
            except BaseException as e:
                try:
                    if str(e).count('Cannot connect to proxy'):
                        need_retest = True
                    else:
                        self.logger.ex(e)
                except UnicodeDecodeError:
                    pass
                except UnboundLocalError:
                    self.logger.ex(e)

            finally:
                pass
