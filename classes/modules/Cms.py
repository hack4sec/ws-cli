# -*- coding: utf-8 -*-
"""
This is part of WebScout software
Docs EN: http://hack4sec.pro/wiki/index.php/WebScout_en
Docs RU: http://hack4sec.pro/wiki/index.php/WebScout
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

Class of CMS module
"""
from __future__ import division

import time
import os
import json
import re


from classes.Registry import Registry
from classes.jobs.CmsJob import CmsJob
from classes.models.HostsModel import HostsModel
from classes.models.HostsInfoModel import HostsInfoModel
from classes.models.UrlsModel import UrlsModel
from classes.models.UrlsBaseModel import UrlsBaseModel
from classes.models.CmsModel import CmsModel
from classes.kernel.WSModule import WSModule
from classes.kernel.WSException import WSException
from classes.kernel.WSCounter import WSCounter
from classes.kernel.WSOption import WSOption
from classes.threads.CmsThread import CmsThread
from classes.threads.SCmsThread import SCmsThread


class Cms(WSModule):
    """ Class of CMS module """
    model = None
    log_path = '/dev/null'
    options = {}
    logger_enable = True
    logger_name = 'cms'
    logger_have_items = True
    time_count = True
    options_sets = {
        "scan": {
            "threads": WSOption(
                "threads",
                "Threads count, default 10",
                int(Registry().get('config')['main']['default_threads']),
                False,
                ['--threads']
            ),
            "host": WSOption(
                "host",
                "Traget host for scan",
                "",
                True,
                ['--host']
            ),
            "method": WSOption(
                "method",
                "Requests method (default - HEAD)",
                "HEAD",
                False,
                ['--method']
            ),
            "protocol": WSOption(
                "protocol",
                "Protocol http or https (default - http)",
                "http",
                False,
                ['--protocol']
            ),
            "url": WSOption(
                "url",
                "Url for scan, default /",
                "/",
                False,
                ['--url']
            ),
            "not-found-re": WSOption(
                "not-found-re",
                "Regex for detect 'Not found' response (404)",
                "",
                False,
                ['--not-found-re']
            ),
            "not-found-size": WSOption(
                "not-found-size",
                "Size in bytes for detect 'Not found' response (404)",
                "-1",
                False,
                ['--not-found-size']
            ),
            "not-found-codes": WSOption(
                "not-found-codes",
                "Custom codes for detect 'Not found' response (404)",
                "404",
                False,
                ['--not-found-codes']
            ),
            "delay": WSOption(
                "delay",
                "Deley for every thread between requests (secs)",
                "0",
                False,
                ['--delay']
            ),
            "selenium": WSOption(
                "selenium",
                "Use Selenium for scanning",
                "",
                False,
                ['--selenium']
            ),
            "ddos-detect-phrase": WSOption(
                "ddos-detect-phrase",
                "Phrase for detect DDoS protection",
                "",
                False,
                ['--ddos-detect-phrase']
            ),
            "ddos-human-action": WSOption(
                "ddos-human-action",
                "Phrase for detect human action need",
                "",
                False,
                ['--ddos-human-action']
            ),
            "browser-recreate-re": WSOption(
                "browser-recreate-re",
                "Regex for recreate browser with new proxy",
                "",
                False,
                ['--browser-recreate-re']
            ),
            "proxies": WSOption(
                "proxies",
                "File with list of proxies",
                "",
                False,
                ['--proxies']
            ),
            "headers-file": WSOption(
                "headers-file",
                "File with list of HTTP headers",
                "",
                False,
                ['--headers-file']
            ),
        },
    }

    def validate_main(self):
        """ Check users params """
        super(Cms, self).validate_main()

    def scan_action(self):
        """ Scan action of module """
        self.enable_logger()
        self.validate_main()
        self.pre_start_inf()

        self.model = CmsModel()

        if self.options['proxies'].value:
            Registry().get('proxies').load(self.options['proxies'].value)

        result = []

        q = CmsJob()
        for item in self.model.all_paths_list():
            q.put(item.strip())

        self.logger.log("Loaded {0} variants.".format(q.qsize()))

        counter = WSCounter(1, 60, q.qsize())

        w_thrds = []
        for _ in range(int(self.options['threads'].value)):
            if self.options['selenium'].value:
                worker = SCmsThread(
                    q,
                    self.options['host'].value,
                    self.options['url'].value,
                    self.options['protocol'].value.lower(),
                    self.options['method'].value.lower(),
                    self.options['not-found-re'].value,
                    self.options['delay'].value,
                    self.options['ddos-detect-phrase'].value,
                    self.options['ddos-human-action'].value,
                    self.options['browser-recreate-re'].value,
                    counter,
                    result
                )
            else:
                worker = CmsThread(
                    q,
                    self.options['host'].value,
                    self.options['url'].value,
                    self.options['protocol'].value.lower(),
                    self.options['method'].value.lower(),
                    self.options['not-found-re'].value,
                    self.options['not-found-size'].value,
                    self.options['not-found-codes'].value.lower(),
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
            for worker in w_thrds:
                if Registry().get('proxy_many_died'):
                    worker.done = True
                    time.sleep(3)

                if worker.done or Registry().get('positive_limit_stop'):
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
                            worker = SCmsThread(
                                q,
                                self.options['host'].value,
                                self.options['url'].value,
                                self.options['protocol'].value.lower(),
                                self.options['method'].value.lower(),
                                self.options['not-found-re'].value,
                                self.options['delay'].value,
                                self.options['ddos-detect-phrase'].value,
                                self.options['ddos-human-action'].value,
                                self.options['browser-recreate-re'].value,
                                counter,
                                result
                            )
                        else:
                            worker = CmsThread(
                                q,
                                self.options['host'].value,
                                self.options['url'].value,
                                self.options['protocol'].value.lower(),
                                self.options['method'].value.lower(),
                                self.options['not-found-re'].value,
                                self.options['not-found-codes'].value.lower(),
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
                print "{0} {1}".format(result[-i]['code'], result[-i]['path'])
            exit(0)

        pid = Registry().get('pData')['id']

        host_id = HostsModel().get_id_by_name(pid, self.options['host'].value)
        Urls = UrlsModel()
        UrlsBase = UrlsBaseModel()
        if int(Registry().get('config')['main']['put_data_into_db']):
            self.logger.log("\nInsert result info in DB...")

            _all = 0
            added = 0
            HostsInfo = HostsInfoModel()
            to_hosts_info = []
            hash_ids = []
            for link in result:
                hash_ids.append(self.model.get_hash_id_by_path(link['path']))
                _all += 1
                if Urls.add(pid, host_id, link['path'], '', link['code'], 0, 'cms'):
                    added += 1
                UrlsBase.add_url(host_id, link['path'])
            self.logger.log("\nFound {0} URLs, inserted in database (new) - {1}.".format(_all, added))

            cms_list = self.model.cms_list()
            for cms_id in self.model.get_cms_by_hash_ids(hash_ids):
                cms_paths = self.model.get_cms_paths(cms_id)

                current_count = 0
                for link in result:
                    if link['path'] in cms_paths:
                        current_count += 1
                percent = int(current_count / len(cms_paths) * 100)

                if int(Registry().get('config')['cms']['percent']) <= percent:
                    to_hosts_info.append({'name': cms_list[cms_id], 'percent': percent})
                    self.logger.log("{0}\t{1}%".format(cms_list[cms_id], percent))

            if len(to_hosts_info):
                HostsInfo.set_info(pid, host_id, 'cms', json.dumps(to_hosts_info))
        else:
            hash_ids = []
            for link in result:
                hash_ids.append(self.model.get_hash_id_by_path(link['path']))

            cms_list = self.model.cms_list()
            for cms_id in self.model.get_cms_by_hash_ids(hash_ids):
                cms_paths = self.model.get_cms_paths(cms_id)

                current_count = 0
                for link in result:
                    if link['path'] in cms_paths:
                        current_count += 1
                percent = int(current_count / len(cms_paths) * 100)

                if int(Registry().get('config')['cms']['percent']) <= percent:
                    self.logger.log("{0}\t{1}%".format(cms_list[cms_id], percent))

        self.done = True
