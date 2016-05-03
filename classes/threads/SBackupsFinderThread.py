# -*- coding: utf-8 -*-
""" Thread class for BF module (selenium) """

import Queue
import time
import re

from selenium.common.exceptions import TimeoutException

from classes.Registry import Registry
from classes.threads.SeleniumThread import SeleniumThread


class SBackupsFinderThread(SeleniumThread):
    """ Thread class for BF module (selenium) """
    queue = None
    method = None
    url = None
    counter = None
    last_action = 0

    def __init__(
            self, queue, domain, protocol, method, not_found_re,
            delay, ddos_phrase, ddos_human, recreate_re, counter, result
    ):
        super(SBackupsFinderThread, self).__init__()
        self.queue = queue
        self.method = method if not (len(not_found_re) and method.lower() == 'head') else 'get'
        self.domain = domain
        self.result = result
        self.counter = counter
        self.protocol = protocol
        self.not_found_re = False if not len(not_found_re) else re.compile(not_found_re)
        self.done = False
        self.http = Registry().get('http')
        self.delay = int(delay)
        self.ddos_phrase = ddos_phrase
        self.ddos_human = ddos_human
        self.recreate_re = False if not len(recreate_re) else re.compile(recreate_re)

        self.logger = Registry().get('logger')

        Registry().set('url_for_proxy_check', "{0}://{1}".format(protocol, domain))

        self.browser_create()

    def run(self):
        """ Run thread """
        while not self.done:
            self.last_action = int(time.time())

            if self.delay:
                time.sleep(self.delay)

            try:
                word = self.queue.get()
                self.counter.up()

                url = "{0}://{1}{2}".format(self.protocol, self.domain, word)

                self.browser.get(url)

                if self.recreate_re and self.recreate_re.findall(self.browser.page_source):
                    #self.queue.task_done(word)
                    #self.queue.put(word)
                    self.browser_close()
                    self.browser_create()
                    continue

                if not self.not_found_re.findall(self.browser.page_source):
                    self.result.append(word)

                self.logger.item(word, self.browser.page_source)

                if len(self.result) >= int(Registry().get('config')['main']['positive_limit_stop']):
                    Registry().set('positive_limit_stop', True)

                #self.queue.task_done(word)
            except Queue.Empty:
                self.done = True
                break
            except TimeoutException as e:
                self.queue.put(word)
                self.browser_close()
                self.browser_create()
                continue
            except BaseException as e:
                #self.queue.task_done(word)
                if not str(e).count('Timed out waiting for page load'):
                    self.logger.ex(e)
                if str(e).count("Connection refused"):
                    self.queue.put(word)
                    self.browser_close()
                    self.browser_create()
            self.up_requests_count()

        self.browser_close()
