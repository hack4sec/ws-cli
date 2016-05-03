# -*- coding: utf-8 -*-
""" Class for work with proxy """

import random
import requests

from classes.Registry import Registry
from libs.common import file_to_list

class Proxies(object):
    """ Class for work with proxy """
    _proxies = []
    died_limit = 0
    died_count = 0

    def __init__(self):
        self.died_limit = int(Registry().get('config')['main']['proxies_died_limit'])

    def load(self, path):
        """ Load proxy-list from path """
        proxies = file_to_list(path)

        for proxy in proxies:
            if len(proxy):
                self._proxies.append(proxy)

    def get_proxy(self):
        """ Get actual proxy """
        proxy = self._proxies[random.randint(0, len(self._proxies)-1)] if len(self._proxies) else False
        return proxy if proxy is False or self.check_live(proxy) else self.get_proxy()

    def check_live(self, proxy):
        """ Check proxy is it live """
        try:
            proxies = {
                "http": "http://" + proxy,
                "https": "https://" + proxy,
            }
            if Registry().isset('url_for_proxy_check'):
                requests.get(Registry().get('url_for_proxy_check'), timeout=10, allow_redirects=False, proxies=proxies)
            else:
                requests.get('http://google.com', timeout=10, allow_redirects=False, proxies=proxies)
            #print 'Proxy {0} is alive'.format(proxy)
            self.died_count = 0
            return True
        except BaseException:
            #print 'Proxy {0} is dead'.format(proxy)
            self.died_count += 1
            if self.died_count >= self.died_limit:
                Registry().set('proxy_many_died', True)
        return False
