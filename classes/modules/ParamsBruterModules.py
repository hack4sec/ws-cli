# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Common module class form Dafs* modules
"""
import time
import re
import os
from urlparse import urlparse

from classes.Registry import Registry
from classes.kernel.WSModule import WSModule
from classes.kernel.WSException import WSException
from classes.kernel.WSCounter import WSCounter
from classes.models.HostsModel import HostsModel
from classes.models.UrlsBaseModel import UrlsBaseModel
from classes.models.UrlsModel import UrlsModel
from classes.jobs.ParamsBruterJob import ParamsBruterJob
from classes.threads.ParamsBruterThread import ParamsBruterThread
from classes.threads.SParamsBruterThread import SParamsBruterThread

class ParamsBruterModules(WSModule):
    """ Common module class form Dafs* modules """
    logger_enable = True
    logger_name = 'params-bruter'
    logger_have_items = True

    def load_objects(self, queue):
        """ Method for prepare check objects, here abstract """
        pass

    def validate_main(self):
        """ Check users params """
        super(ParamsBruterModules, self).validate_main()

        if self.options['url'].value[0] != '/':
            raise WSException("URL must start from the root ('/') !")

    def brute_action(self):
        #TODO тип того что суём в параметры
        #TODO может обрабатывать url-символы в имени параметров или чекать чтоб там не было мусора?
        """ Scan action of module """
        self.enable_logger()
        self.validate_main()
        self.pre_start_inf()

        if self.options['proxies'].value:
            Registry().get('proxies').load(self.options['proxies'].value)

        result = []

        q = ParamsBruterJob()

        loaded = self.load_objects(q)

        self.logger.log(
            "Loaded {0} words ({1}-{2}) from all {3}.".format(
                (loaded['end'] - loaded['start']), loaded['start'], loaded['end'], loaded['all'])
            if (int(self.options['parts'].value) and int(self.options['part'].value)) else
            "Loaded {0} words from source.".format(loaded['all'])
        )

        counter = WSCounter(50, 3000, loaded['all'] if not loaded['end'] else loaded['end']-loaded['start'])

        w_thrds = []
        for _ in range(int(self.options['threads'].value)):
            if self.options['selenium'].value:
                worker = SParamsBruterThread(
                    q,
                    self.options['protocol'].value,
                    self.options['host'].value,
                    self.options['url'].value,
                    self.options['max-params-length'].value,
                    self.options['value'].value,
                    self.options['method'].value.lower(),
                    self.options['msymbol'].value,
                    self.options['not-found-re'].value,
                    self.options['delay'].value,
                    self.options['ddos-detect-phrase'].value,
                    self.options['ddos-human-action'].value,
                    self.options['browser-recreate-re'].value,
                    self.options['ignore-words-re'].value,

                    counter,
                    result
                )
            else:
                worker = ParamsBruterThread(
                    q,
                    self.options['protocol'].value,
                    self.options['host'].value,
                    self.options['url'].value,
                    self.options['max-params-length'].value,
                    self.options['value'].value,
                    self.options['method'].value.lower(),
                    self.options['msymbol'].value,
                    self.options['not-found-re'].value,
                    self.options['not-found-size'].value,
                    self.options['not-found-codes'].value.lower(),
                    self.options['retest-codes'].value.lower(),
                    self.options['delay'].value,
                    self.options['ignore-words-re'].value,
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
                        if self.options['selenium'].value:
                            worker = SParamsBruterThread(
                                q,
                                self.options['protocol'].value,
                                self.options['host'].value,
                                self.options['url'].value,
                                self.options['max-params-length'].value,
                                self.options['value'].value,
                                self.options['method'].value.lower(),
                                self.options['msymbol'].value,
                                self.options['not-found-re'].value,
                                self.options['delay'].value,
                                self.options['ddos-detect-phrase'].value,
                                self.options['ddos-human-action'].value,
                                self.options['browser-recreate-re'].value,
                                self.options['ignore-words-re'].value,

                                counter,
                                result
                            )
                        else:
                            worker = ParamsBruterThread(
                                q,
                                self.options['protocol'].value,
                                self.options['host'].value,
                                self.options['url'].value,
                                self.options['max-params-length'].value,
                                self.options['value'].value,
                                self.options['method'].value.lower(),
                                self.options['msymbol'].value,
                                self.options['not-found-re'].value,
                                self.options['not-found-size'].value,
                                self.options['not-found-codes'].value.lower(),
                                self.options['retest-codes'].value.lower(),
                                self.options['delay'].value,
                                self.options['ignore-words-re'].value,
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

        self.logger.log("\n")
        for result_row in result:
            self.logger.log(result_row)

        self.done = True
