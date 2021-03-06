# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Thread class for FormBruter module
"""

import threading
import Queue
import time
import copy

from requests.exceptions import ChunkedEncodingError, ConnectionError

from classes.Registry import Registry
from classes.threads.HttpThread import HttpThread

class FormBruterThread(HttpThread):
    """ Thread class for FormBruter module """
    queue = None
    method = None
    url = None
    mask_symbol = None
    counter = None
    last_action = 0
    logger = None
    retested_words = None
    last_action = 0

    def __init__(
            self, queue, protocol, host, url, false_phrase, true_phrase, retest_codes, delay,
            confstr, first_stop, login, pass_min_len, pass_max_len, pass_found, counter, result
    ):
        threading.Thread.__init__(self)
        self.retested_words = {}
        self.queue = queue
        self.protocol = protocol.lower()
        self.host = host
        self.url = url
        self.false_phrase = false_phrase
        self.true_phrase = true_phrase
        self.delay = int(delay)
        self.confstr = confstr
        self.first_stop = first_stop
        self.login = login
        self.counter = counter
        self.result = result
        self.retest_codes = list(set(retest_codes.split(','))) if len(retest_codes) else []
        self.pass_found = pass_found
        self.done = False
        self.logger = Registry().get('logger')
        self.http = copy.deepcopy(Registry().get('http'))
        self.http.every_request_new_session = True
        self.pass_min_len = int(pass_min_len)
        self.pass_max_len = int(pass_max_len)
        self.retest_delay = int(Registry().get('config')['form_bruter']['retest_delay'])
        self.retest_limit = int(Registry().get('config')['form_bruter']['retest_limit'])

    def _make_conf_from_str(self, confstr):
        result = {}
        tmp = confstr.split("&")
        for tmp_row in tmp:
            field, value = tmp_row.split("=")
            result[field] = value
        return result

    def _fill_conf(self, conf, login, password):
        for field in conf.keys():
            conf[field] = conf[field].replace("^USER^", login).replace("^PASS^", password)
        return conf

    def run(self):
        """ Run thread """
        need_retest = False
        word = False

        conf = self._make_conf_from_str(self.confstr)

        while not self.pass_found and not self.done:
            try:
                self.last_action = int(time.time())

                if self.pass_found:
                    self.done = True
                    break

                if self.delay:
                    time.sleep(self.delay)

                if not need_retest:
                    word = self.queue.get()
                    self.counter.up()

                if (self.pass_min_len and len(word) < self.pass_min_len) or \
                        (self.pass_max_len and len(word) > self.pass_max_len):
                    continue

                work_conf = self._fill_conf(dict(conf), self.login, word)
                try:
                    resp = self.http.post(
                        self.protocol + "://" + self.host + self.url, data=work_conf, allow_redirects=True
                    )
                except ConnectionError:
                    need_retest = True
                    self.http.change_proxy()
                    continue

                if self.is_retest_need(word, resp):
                    time.sleep(self.retest_delay)
                    need_retest = True
                    continue

                positive_item = False
                if (len(self.false_phrase) and
                        not resp.content.count(self.false_phrase)) or \
                        (len(self.true_phrase) and resp.content.count(self.true_phrase)):
                    self.result.append({'word': word, 'content': resp.content})
                    positive_item = True

                    self.check_positive_limit_stop(self.result)

                self.log_item(word, resp, positive_item)

                if positive_item and int(self.first_stop):
                    self.done = True
                    self.pass_found = True
                    break

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
                        self.logger.log(str(word) + " " + str(e))
                except UnicodeDecodeError:
                    pass
                except UnboundLocalError:
                    self.logger.ex(e)
            finally:
                pass
