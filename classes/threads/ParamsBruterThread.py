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

from classes.Registry import Registry
from libs.common import is_binary_content_type


class ParamsBruterThread(threading.Thread):
    """ Thread class for Dafs modules """
    queue = None
    method = None
    template = None
    mask_symbol = None
    counter = None
    retested_words = None
    last_action = 0
    retest_limit = int(Registry().get('config')['dafs']['retest_limit'])
    ignore_words_re = None

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

        self.http = copy.deepcopy(Registry().get('http'))
        self.logger = Registry().get('logger')

    def is_response_content_binary(self, resp):
        return resp is not None \
            and 'content-type' in resp.headers \
            and is_binary_content_type(resp.headers['content-type'])

    def is_response_right(self, resp):
        response_headers_text = ''
        for header in resp.headers:
            response_headers_text += '{0}: {1}\r\n'.format(header, resp.headers[header])

        binary_content = self.is_response_content_binary(resp)

        return resp is not None \
                and (self.not_found_size == -1 or self.not_found_size != len(resp.content)) \
                and str(resp.status_code) not in self.not_found_codes \
                and not (not binary_content and self.not_found_re and (
                    self.not_found_re.findall(resp.content) or
                    self.not_found_re.findall(response_headers_text)
                ))
    def run(self):
        """ Run thread """
        need_retest = False
        last_word = ""
        queue_is_empty = False

        while not self.done:
            self.last_action = int(time.time())

            if self.delay:
                time.sleep(self.delay)

            try:
                if not need_retest:
                    params_str = "" if not len(last_word) else "{0}={1}&".format(last_word, self.value)
                    last_word = ""
                    while len(params_str) < self.max_params_length:
                        try:
                            word = self.queue.get()
                        except Queue.Empty:
                            queue_is_empty = True
                            break

                        if not len(word.strip()) or (self.ignore_words_re and self.ignore_words_re.findall(word)):
                            continue

                        self.counter.up()

                        params_str += "{0}={1}&".format(word, self.value)

                        last_word = word
                    params_str = params_str[:-(len(last_word)+3)]

                try:
                    if self.method == 'get':
                        resp = self.http.get(self.protocol + "://" + self.host + self.url + params_str)
                    else:
                        resp = self.http.post(
                            self.protocol + "://" + self.host + self.url, data=params_str,
                            headers={'Content-Type': 'application/x-www-form-urlencoded'})
                except ConnectionError:
                    need_retest = True
                    self.http.change_proxy()
                    continue

                if resp is not None and len(self.retest_codes) and str(resp.status_code) in self.retest_codes:
                    if params_str not in self.retested_words.keys():
                        self.retested_words[params_str] = 0
                    self.retested_words[params_str] += 1

                    if self.retested_words[params_str] <= self.retest_limit:
                        need_retest = True
                        time.sleep(int(Registry().get('config')['dafs']['retest_delay']))
                        continue

                positive_item = False
                if self.is_response_right(resp):
                    right_response_binary_content = self.is_response_content_binary(resp)
                    param_found = False
                    for one_param in params_str.split("&"):
                        try:
                            if self.method == 'get':
                                resp = self.http.get(self.protocol + "://" + self.host + self.url + one_param)
                            else:
                                resp = self.http.post(
                                    self.protocol + "://" + self.host + self.url, data=one_param,
                                    headers={'Content-Type': 'application/x-www-form-urlencoded'})
                        except ConnectionError:
                            need_retest = True
                            self.http.change_proxy()
                            continue

                        if self.is_response_right(resp):
                            self.result.append(one_param)
                            param_found = True
                            found_item = one_param
                            right_response_binary_content = self.is_response_content_binary(resp)

                    if param_found is False:
                        self.result.append(params_str)
                        found_item = params_str

                    positive_item = True

                    self.logger.item(
                        found_item, resp.content if resp is not None else "",
                        right_response_binary_content, positive=positive_item)

                if len(self.result) >= int(Registry().get('config')['main']['positive_limit_stop']):
                    Registry().set('positive_limit_stop', True)

                need_retest = False

                if queue_is_empty:
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
