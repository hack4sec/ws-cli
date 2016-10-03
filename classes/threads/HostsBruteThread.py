# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Thread class for HostsBrute modules
"""

import threading
import Queue
import time
import copy
import pprint

from requests.exceptions import ChunkedEncodingError, ConnectionError

from classes.Registry import Registry


class HostsBruteThread(threading.Thread):
    """ Thread class for HostsBrute modules """
    queue = None
    method = None
    url = None
    mask_symbol = None
    counter = None
    retested_words = None
    last_action = 0
    retest_limit = int(Registry().get('config')['hosts_brute']['retest_limit'])

    def __init__(
            self, queue, protocol, host, template, mask_symbol,
            false_phrase, retest_codes, delay, counter, result):
        threading.Thread.__init__(self)
        self.retested_words = {}

        self.queue = queue
        self.protocol = protocol.lower()
        self.host = host
        self.template = template
        self.mask_symbol = mask_symbol
        self.counter = counter
        self.result = result
        self.done = False

        self.false_phrase = false_phrase
        self.retest_codes = list(set(retest_codes.split(','))) if len(retest_codes) else []

        self.delay = int(delay)

        self.http = copy.deepcopy(Registry().get('http'))
        self.logger = Registry().get('logger')

        self.method = 'get'

    def run(self):
        """ Run thread """
        req_func = getattr(self.http, self.method)
        need_retest = False
        word = False

        while not self.done:
            self.last_action = int(time.time())

            if self.delay:
                time.sleep(self.delay)

            try:
                if not need_retest:
                    word = self.queue.get()
                    self.counter.up()

                try:
                    hostname = self.template.replace(self.mask_symbol, word)
                except UnicodeDecodeError:
                    self.logger.log(
                        "URL build error (UnicodeDecodeError) with word '{0}', skip it".format(pprint.pformat(word)),
                        _print=False
                    )
                    continue

                try:
                    resp = req_func(self.protocol + "://" + self.host, headers={'host': hostname})
                except ConnectionError:
                    need_retest = True
                    self.http.change_proxy()
                    continue

                binary_content = False

                if resp is not None and len(self.retest_codes) and str(resp.status_code) in self.retest_codes:
                    if word not in self.retested_words.keys():
                        self.retested_words[word] = 0
                    self.retested_words[word] += 1

                    if self.retested_words[word] <= self.retest_limit:
                        need_retest = True
                        time.sleep(int(Registry().get('config')['hosts_brute']['retest_delay']))
                        continue

                if resp is not None and not resp.text.count(self.false_phrase):
                    self.result.append(hostname)

                self.logger.item(word, resp.content if not resp is None else "", binary_content)

                if len(self.result) >= int(Registry().get('config')['main']['positive_limit_stop']):
                    Registry().set('positive_limit_stop', True)

                need_retest = False
            except Queue.Empty:
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
