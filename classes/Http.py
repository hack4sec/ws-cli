# -*- coding: utf-8 -*-
""" Class for common HTTP work """

import requests
from classes.Registry import Registry


class HttpMaxSizeException(BaseException):
    """ Exception class for max-size error """
    pass


class Http(object):
    """ Class for common HTTP work """
    verify = False
    allow_redirects = False
    headers = None
    config = None
    sess = None
    noscan_content_types = []
    scan_content_types = []
    # Common for all class copies dict with errors
    errors = {'maxsize': [], 'noscan_content_types': [], 'scan_content_types': []}
    current_proxy = None
    current_proxy_count = 0
    every_request_new_session = False

    def __init__(self, verify=False, allow_redirects=False, headers=None):
        #self.errors = {'maxsize': [], 'noscan_content_types': [], 'scan_content_types': []}
        self.headers = {}
        self.verify = verify
        self.allow_redirects = allow_redirects
        self.headers = {} if headers is None else headers
        self.session = requests.Session()

    def set_allowed_types(self, types):
        """ Set allowed contnent types """
        self.scan_content_types = types

    def set_denied_types(self, types):
        """ Set denied contnent types """
        self.noscan_content_types = types

    def change_proxy(self):
        self.current_proxy = Registry().get('proxies').get_proxy()

    def get_current_proxy(self):
        """ Check current proxy, get next if need (max requests per proxy made) """
        if self.current_proxy_count >= int(Registry().get('config')['main']['requests_per_proxy']):
            self.current_proxy = None
            self.current_proxy_count = 0

        if not self.current_proxy:
            #self.current_proxy = Registry().get('proxies').get_proxy()
            self.change_proxy()

        self.current_proxy_count += 1

        return {
            "http": "http://" + self.current_proxy,
            "https": "http://" + self.current_proxy,
        } if self.current_proxy else None

    def get(self, url, verify=None, allow_redirects=None, headers=None):
        """ HTTP GET request """
        if self.every_request_new_session:
            self.session = requests.Session()
        verify = self.verify if verify is None else verify
        allow_redirects = self.allow_redirects if allow_redirects is None else allow_redirects
        headers = self.headers if headers is None else headers

        resp = self.session.get(
            url,
            verify=verify,
            allow_redirects=allow_redirects,
            headers=headers,
            stream=True,
            proxies=self.get_current_proxy()
        )

        if 'content-length' in resp.headers and \
                        int(resp.headers['content-length']) > int(Registry().get('config')['main']['max_size']):
            self.errors['maxsize'].append(
                "URL {0} has size {1} bytes, but limit in config - {2} bytes".
                format(
                    url,
                    resp.headers['content-length'],
                    Registry().get('config')['main']['max_size']
                )
            )
            resp = None

        if resp and 'content-type' in resp.headers and (len(self.scan_content_types) or len(self.noscan_content_types)):
            if len(self.noscan_content_types):
                for _type in self.noscan_content_types:
                    if resp.headers['content-type'].lower().count(_type.lower()):
                        self.errors['noscan_content_types'].append(
                            "URL {0} have denied content type  - {1}".format(url, _type)
                        )
                        resp = None
                        break
            if resp and len(self.scan_content_types):
                allowed = False
                for _type in self.scan_content_types:
                    if resp.headers['content-type'].lower().count(_type.lower()):
                        allowed = True
                        break
                if not allowed:
                    self.errors['scan_content_types'].append(
                        "URL {0} have not allowed content type  - {1}".format(url, resp.headers['content-type'])
                    )
                    resp = None

        return resp

    def post(self, url, data=None, verify=None, allow_redirects=None, headers=None):
        """ HTTP POST request """
        if self.every_request_new_session:
            self.session = requests.Session()
        verify = self.verify if verify is None else verify
        allow_redirects = self.allow_redirects if allow_redirects is None else allow_redirects
        headers = self.headers if headers is None else headers

        resp = self.session.post(
            url,
            data=data,
            verify=verify,
            allow_redirects=allow_redirects,
            headers=headers,
            stream=True,
            proxies=self.get_current_proxy()
        )
        if 'content-length' in resp.headers and \
                        int(resp.headers['content-length']) > int(Registry().get('config')['main']['max_size']):
            self.errors['maxsize'].append(
                "URL {0} has size {1} bytes, but limit in config - {2} bytes".
                format(
                    url,
                    resp.headers['content-length'],
                    Registry().get('config')['main']['max_size']
                )
            )
            resp = None

        return resp

    def head(self, url, verify=None, allow_redirects=None, headers=None):
        """ HTTP HEAD request """
        if self.every_request_new_session:
            self.session = requests.Session()
        verify = self.verify if verify is None else verify
        allow_redirects = self.allow_redirects if allow_redirects is None else allow_redirects
        headers = self.headers if headers is None else headers

        resp = self.session.head(
            url,
            verify=verify,
            allow_redirects=allow_redirects,
            headers=headers,
            proxies=self.get_current_proxy()
        )

        if 'content-length' in resp.headers and \
                        int(resp.headers['content-length']) > int(Registry().get('config')['main']['max_size']):
            self.errors['maxsize'].append(
                "URL {0} has size {1} bytes, but limit in config - {2} bytes".\
                format(
                    url,
                    resp.headers['content-length'],
                    Registry().get('config')['main']['max_size']
                )
            )
            resp = None
        return resp
