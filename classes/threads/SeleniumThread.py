# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Common thread class for selenium threads
"""
import os
import random
import threading
import shutil
import time

from selenium import webdriver
from selenium.webdriver.common.proxy import ProxyType, Proxy
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

from classes.Registry import Registry
from classes.SeleniumBrowser import SeleniumBrowser

class SeleniumThread(threading.Thread):
    """ Common thread class for selenium threads """
    requests_count = 0
    proxy_using = False
    browser = None

    def up_requests_count(self):
        """ Up requests counter """
        self.requests_count += 1
        if self.proxy_using and self.requests_count >= int(Registry().get('config')['main']['requests_per_proxy']):
            #print "Recreating browser"
            self.browser_close()
            self.browser_create()
            self.requests_count = 0

    def browser_create(self, retry_counter = 0):
        """ Create a browser """
        if retry_counter >= int(Registry().get('config')['selenium']['browser_recreate_errors_limit']):
            raise Exception("WebDriver can`t create browser. Check errors log selenium settings.")

        self_num = random.randint(0, 99999)

        myProxy = Registry().get('proxies').get_proxy()
        if myProxy:
            proxy = Proxy({
                'proxyType': ProxyType.MANUAL,
                'httpProxy': myProxy,
                'ftpProxy': myProxy,
                'sslProxy': myProxy,
                'noProxy': ''
                })
            self.proxy_using = True
        else:
            #print "No proxy"
            proxy = None
            self.proxy_using = False

        profile_path = '/tmp/wr-selenium-{0}/'.format(self_num)
        if os.path.exists(profile_path):
            shutil.rmtree(profile_path)

        if not os.path.exists(profile_path):
            os.mkdir(profile_path)

        profile = webdriver.FirefoxProfile(profile_path)

        if Registry().get('config')['selenium']['css_load'] != '1':
            profile.set_preference('permissions.default.stylesheet', 2)
        if Registry().get('config')['selenium']['images_load'] != '1':
            profile.set_preference('permissions.default.image', 2)
        if Registry().get('config')['selenium']['flash_load'] != '1':
            profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')

        profile.set_preference("browser.startup.homepage", "about:blank")
        profile.set_preference("startup.homepage_welcome_url", "about:blank")
        profile.set_preference("startup.homepage_welcome_url.additional", "about:blank")

        fo = open('/tmp/firefox-run-{0}.log'.format(self_num), "w")
        binary = FirefoxBinary(firefox_path=Registry().get('config')['selenium']['firefox_path'], log_file=fo)
        try:
            self.browser = SeleniumBrowser(
                profile,
                firefox_binary=binary,
                ddos_phrase=self.ddos_phrase,
                proxy=proxy,
                ddos_human=self.ddos_human,
            )
        except WebDriverException as e:
            self.logger.ex(e)
            self.logger.log("Re-trying. Browser creation error: " + str(e))

            shutil.rmtree(profile_path)
            time.sleep(5)

            retry_counter += 1

            return self.browser_create(retry_counter)

        self.browser.set_page_load_timeout(Registry().get('config')['selenium']['timeout_page_load'])
        self.browser.implicitly_wait(Registry().get('config')['selenium']['timeout_page_load'])

    def browser_close(self):
        """ Quit browser """
        try:
            self.browser.close()
            self.browser.quit()
            self.browser.binary.process.kill()

            if os.path.exists(self.browser.profile_path.replace('webdriver-py-profilecopy', '')):
                shutil.rmtree(self.browser.profile_path.replace('webdriver-py-profilecopy', ''))
        except BaseException:
            pass
