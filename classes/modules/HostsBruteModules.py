# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Common module class form HostsBrute* modules
"""
import time
from urlparse import urlparse

from classes.Registry import Registry
from classes.kernel.WSModule import WSModule
from classes.kernel.WSException import WSException
from classes.kernel.WSCounter import WSCounter
from classes.models.HostsModel import HostsModel
from classes.models.UrlsBaseModel import UrlsBaseModel
from classes.models.UrlsModel import UrlsModel
from classes.jobs.HostsBruteJob import HostsBruteJob
from classes.threads.HostsBruteThread import HostsBruteThread

class HostsBruteModules(WSModule):
    """ Common module class form HostsBrute* modules """
    logger_enable = True
    logger_name = 'hosts'
    logger_have_items = True

    def load_objects(self, queue):
        """ Method for prepare check objects, here abstract """
        pass

    def _insert_urls(self, urls):
        """ Add found urls in db """
        UrlsBase = UrlsBaseModel()
        pid = Registry().get('pData')['id']

        host_id = HostsModel().get_id_by_name(pid, self.options['host'].value)
        Urls = UrlsModel()

        added = 0
        for url in urls:
            if Urls.add(pid, host_id, url['url'], '', url['code'], url['time'], 'dafs'):
                added += 1

            paths = urlparse(url['url']).path.split("/")
            while len(paths) != 1:
                del paths[-1]
                if Urls.add(pid, host_id, "/".join(paths) + "/", '', 0, 0, 'dafs'):
                    added += 1
            UrlsBase.add_url(host_id, url['url'])

        return added

    def validate_main(self):
        """ Check users params """
        super(HostsBruteModules, self).validate_main()

        if not self.options['template'].value.count(self.options['msymbol'].value):
            raise WSException(
                "Template '{0}' not contains msymbol ({1})".format(
                    self.options['template'].value,
                    self.options['msymbol'].value
                )
            )

    def brute_action(self):
        """ Brute action of module """
        self.enable_logger()
        self.validate_main()
        self.pre_start_inf()

        if self.options['proxies'].value:
            Registry().get('proxies').load(self.options['proxies'].value)

        result = []

        q = HostsBruteJob()

        loaded = self.load_objects(q)

        self.logger.log(
            "Loaded {0} words ({1}-{2}) from all {3}.".format(
                (loaded['end'] - loaded['start']), loaded['start'], loaded['end'], loaded['all'])
            if (int(self.options['parts'].value) and int(self.options['part'].value)) else
            "Loaded {0} words from source.".format(loaded['all'])
        )

        counter = WSCounter(5, 300, loaded['all'] if not loaded['end'] else loaded['end']-loaded['start'])

        w_thrds = []
        for _ in range(int(self.options['threads'].value)):
            worker = HostsBruteThread(
                q,
                self.options['protocol'].value,
                self.options['host'].value,
                self.options['template'].value,
                self.options['msymbol'].value,
                self.options['false-phrase'].value,
                self.options['retest-codes'].value.lower(),
                self.options['delay'].value,
                counter,
                result
            )

            worker.setDaemon(True)
            worker.start()
            w_thrds.append(worker)

            time.sleep(1)

        timeout_threads_count = 0
        while len(w_thrds):
            if Registry().get('proxy_many_died'):
                self.logger.log("Proxy many died, stop scan")

            if Registry().get('proxy_many_died') or Registry().get('positive_limit_stop'):
                worker.done = True
                time.sleep(3)

            for worker in w_thrds:
                if worker.done:
                    del w_thrds[w_thrds.index(worker)]

                if int(time.time()) - worker.last_action > int(Registry().get('config')['main']['kill_thread_after_secs']):
                    self.logger.log(
                        "Thread killed by time, resurected {0} times from {1}".format(
                            timeout_threads_count,
                            Registry().get('config')['main']['timeout_threads_resurect_max_count']
                        )
                    )
                    del w_thrds[w_thrds.index(worker)]

                    if timeout_threads_count <= int(Registry().get('config')['main']['timeout_threads_resurect_max_count']):
                        worker = HostsBruteThread(
                            q,
                            self.options['protocol'].value,
                            self.options['host'].value,
                            self.options['template'].value,
                            self.options['msymbol'].value,
                            self.options['false-phrase'].value,
                            self.options['retest-codes'].value.lower(),
                            self.options['delay'].value,
                            counter,
                            result
                        )

                        worker.setDaemon(True)
                        worker.start()
                        w_thrds.append(worker)

                        timeout_threads_count += 1
            time.sleep(2)

        if Registry().get('positive_limit_stop'):
            self.logger.log("\nMany positive detections. Please, look items logs")
            self.logger.log("Last items:")
            for i in range(1, 5):
                print result[-i]
            exit(0)

        self.logger.log("\nFound {0} hosts:".format(len(result)))
        for host in result:
            self.logger.log("\t" + host)

        self.done = True
