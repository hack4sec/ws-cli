# -*- coding: utf-8 -*-
""" Class of selenium browser - main object for selenium work """

import time

#import selenium.common
from selenium import webdriver
#from selenium.webdriver.common.proxy import *
#from selenium.webdriver.common.action_chains import ActionChains
#from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

class SeleniumBrowser(webdriver.Firefox):
    """ Class of selenium browser - main object for selenium work """
    re_phrases = [
        'ENTITY connectionFailure.longDesc',
    ]
    profile_path = None

    def __init__(self, profile, firefox_binary, ddos_phrase, ddos_human, proxy=None):
        super(SeleniumBrowser, self).__init__(profile, firefox_binary=firefox_binary, proxy=proxy)
        self.ddos_phrase = ddos_phrase
        self.ddos_human = ddos_human
        self.profile_path = profile.path

    def get(self, url, from_blank=True):
        """ Get a url, but with check on recreate browser need and anti-ddos sleep """
        if from_blank:
            super(SeleniumBrowser, self).get("about:blank")
        super(SeleniumBrowser, self).get(url)

        for re_phrase in self.re_phrases:
            if self.page_source.count(re_phrase):
                #print "re-phrase detected"
                time.sleep(5)
                return self.get(url)

        while len(self.ddos_phrase) and self.page_source.count(self.ddos_phrase):
            time.sleep(1)

        if len(self.ddos_human):
            while self.page_source.count(self.ddos_human):
                time.sleep(1)

    def element_exists(self, by, _id):
        """ Method check is element geted by selector exists """
        try:
            self.find_element(by, _id)
        except BaseException:
            return False
        return True

