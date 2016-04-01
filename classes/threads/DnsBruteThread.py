# -*- coding: utf-8 -*-
""" Thread class for DnsBrute* modules """
import time
import Queue
import re
import threading

import dns.query
import dns.message

from classes.Registry import Registry

class DnsBruteThread(threading.Thread):
    """ Thread class for DnsBrute* modules """
    done = False

    def __init__(self, queue, domain, proto, msymbol, dns_srv, delay, result, counter):
        threading.Thread.__init__(self)
        self.queue = queue
        self.domain = domain
        self.proto = proto
        self.dns_srv = dns_srv
        self.counter = counter
        self.msymbol = msymbol
        self.result = result
        self.delay = int(delay)
        self.done = False
        self.logger = Registry().get('logger')

    def run(self):
        """ Run thread """
        ip_re = re.compile(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})")
        ns_resp_re = re.compile(r";ANSWER\s(?P<data>(.|\s)*)\s;AUTHORITY", re.M)

        req_func = getattr(dns.query, self.proto.lower())

        while True:
            host = None
            if self.delay:
                time.sleep(self.delay)
            try:
                host = self.queue.get()

                self.counter.up()
                check_name = self.domain.replace(self.msymbol, host)
                query = dns.message.make_query(check_name, 'A')
                result = req_func(query, self.dns_srv, timeout=5)
                response = ns_resp_re.search(result.to_text())
                if response is not None:
                    for ip in ip_re.findall(response.group('data')):
                        self.result.append({'name': check_name, 'ip': ip, 'dns': self.dns_srv})
                        break

                if len(self.result) >= int(Registry().get('config')['main']['positive_limit_stop']):
                    Registry().set('positive_limit_stop', True)

            except Queue.Empty:
                self.done = True
                break

            except BaseException as e:
                self.logger.ex(e)
                time.sleep(5)

