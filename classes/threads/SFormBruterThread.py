# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Thread class for FormBruter module (selenium)
"""
import Queue
import time

from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from classes.Registry import Registry
from classes.threads.SeleniumThread import SeleniumThread

class SFormBruterThread(SeleniumThread):
    """ Thread class for FormBruter module (selenium) """
    queue = None
    method = None
    url = None
    mask_symbol = None
    counter = None
    retested_words = None
    logger = None
    last_action = 0
    first_page_load = False

    def __init__(
            self, queue, protocol, host, url, false_phrase, true_phrase, delay, ddos_phrase, ddos_human, recreate_phrase,
            conffile, first_stop, login, #reload_form_page,
            pass_found, counter, result
    ):
        super(SFormBruterThread, self).__init__()
        self.retested_words = {}

        self.queue = queue
        self.protocol = protocol.lower()
        self.host = host
        self.url = url
        self.delay = int(delay)
        self.ddos_phrase = ddos_phrase
        self.ddos_human = ddos_human
        self.recreate_phrase = recreate_phrase
        self.conffile = conffile
        self.false_phrase = false_phrase
        self.true_phrase = true_phrase
        self.first_stop = first_stop
        self.login = login
        self.pass_found = pass_found
        self.logger = Registry().get('logger')
        #self.reload_form_page = int(reload_form_page)

        self.browser_create()

        self.counter = counter
        self.result = result
        self.done = False

        Registry().set('url_for_proxy_check', "{0}://{1}".format(protocol, host))

    def parse_brute_config(self, path):
        """ Parse conf file to dict """
        to_return = {}
        have_user = False
        have_pass = False
        have_submit = False

        fh = open(path)
        for line in fh.readlines():
            if not len(line.strip()):
                continue

            point, selector = line.strip().split("    ")
            if point == "^USER^":
                have_user = True
            if point == "^PASS^":
                have_pass = True
            if point == "^SUBMIT^":
                have_submit = True

            to_return[point] = selector
        return to_return

    def run(self):
        """ Run thread """
        need_retest = False
        word = False

        brute_conf = self.parse_brute_config(self.conffile)

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

                #if self.reload_form_page or \
                    #    (not self.browser.element_exists(By.CSS_SELECTOR, brute_conf['^USER^']) or
                    #     not self.browser.element_exists(By.CSS_SELECTOR, brute_conf['^PASS^'])) :
                    #self.browser.get(self.protocol + "://" + self.host + self.url)

                self.browser.get(self.protocol + "://" + self.host + self.url)

                if len(self.recreate_phrase) and self.browser.page_source.lower().count(self.recreate_phrase.lower()):
                    need_retest = True
                    self.browser_close()
                    self.browser_create()
                    continue

                self.browser.find_element(By.CSS_SELECTOR, brute_conf['^USER^']).clear()
                self.browser.find_element(By.CSS_SELECTOR, brute_conf['^USER^']).send_keys(self.login)
                self.browser.find_element(By.CSS_SELECTOR, brute_conf['^PASS^']).clear()
                self.browser.find_element(By.CSS_SELECTOR, brute_conf['^PASS^']).send_keys(word)
                self.browser.find_element(By.CSS_SELECTOR, brute_conf['^SUBMIT^']).click()
                time.sleep(1)

                self.logger.item(word, self.browser.page_source, True)

                if ( (len(self.false_phrase) and not self.browser.page_source.count(self.false_phrase)) or
                         (len(self.true_phrase) and self.browser.page_source.count(self.true_phrase)) ):
                    self.result.append({'word': word, 'content': self.browser.page_source})
                    #self.logger.log("Result: {0}".format(word))

                    if len(self.result) >= int(Registry().get('config')['main']['positive_limit_stop']):
                        Registry().set('positive_limit_stop', True)

                    if int(self.first_stop):
                        self.done = True
                        self.pass_found = True
                        break
                    else:
                        # Иначе старая сессия останется и будет куча false-positive
                        self.browser_close()
                        self.browser_create()
                need_retest = False
            except Queue.Empty:
                self.done = True
                break
            except TimeoutException as e:
                need_retest = True
                self.browser_close()
                self.browser_create()
                continue
            except UnicodeDecodeError as e:
                self.logger.ex(e)
                need_retest = False
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
